import argparse
import pathlib
import sys
import typing

import sierra
from sierra.internal.logger import LogLevel, UniversalLogger
from sierra.package_manager import (
    RepositoryManager, PackageRegistry, PackageSearch, 
    PackageInstaller, PackageUpdater
)



def init_command(args: argparse.Namespace) -> None:
    """Initialize a new Sierra environment."""
    env_name = args.name
    cwd = pathlib.Path.cwd()
    env_path = cwd / env_name
    
    print(f"\n🚀 Initializing Sierra environment: {env_name}\n")
    
    if env_path.exists():
        print(f"⚠️  Directory '{env_name}' already exists.")
        if not args.force:
            print("   Use --force to overwrite or specify a different name.\n")
            return
    
    # Create directory structure
    scripts_path = env_path / "scripts"
    scripts_path.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created directory: {env_path}")
    print(f"✅ Created directory: {scripts_path}")
    
    # Create config.yaml
    config_path = env_path / "config.yaml"
    if not config_path.exists() or args.force:
        config_content = (
            "PATHS:\n"
            "  scripts: ./scripts\n"
            "  output: ./results\n\n"
            "SCRIPTS:\n"
            "  # Add your script configurations here\n"
        )
        config_path.write_text(config_content)
        print(f"✅ Created config: {config_path}")
    
    # Create source file
    source_path = env_path / "source"
    if not source_path.exists():
        source_path.touch()
        print(f"✅ Created source file: {source_path}")
    
    print(f"\n✨ Initialization complete! You can now start adding invokers to '{env_name}/scripts'.\n")


def clean_command(args: argparse.Namespace) -> None:
    """Clean generated files from the environment."""
    env_name = args.env
    cwd = pathlib.Path.cwd()
    env_path = cwd / env_name
    
    if not env_path.exists():
        print(f"\n❌ Environment '{env_name}' does not exist.\n")
        return
    
    print(f"\n🧹 Cleaning environment: {env_name}\n")
    
    # Remove config.yaml
    config_path = env_path / "config.yaml"
    if config_path.exists():
        config_path.unlink()
        print(f"✅ Removed: {config_path}")
    
    # Remove __pycache__
    for pycache in env_path.rglob("__pycache__"):
        import shutil
        shutil.rmtree(pycache)
        print(f"✅ Removed: {pycache}")
    
    print(f"\n✨ Clean complete.\n")


def build_command(args: argparse.Namespace) -> None:
    """Build command to compile Sierra invokers."""
    cwd = pathlib.Path.cwd()
    print(f"Building Sierra project in {cwd}...")
    
    client = setup_client(args)
    
    # Run validation before build
    client.logger.log("🔍 Running pre-build validation", "info")
    checker = client.checker
    issues = checker.validate_all()
    
    # Show issues
    errors = [i for i in issues if i.severity == "error"]
    if errors:
        client.logger.log("❌ Build aborted due to validation errors:", "error")
        for issue in errors:
            print(issue)
        print("\n💡 Fix the errors above and try again.")
        return
    
    # Warnings don't block build
    warnings = [i for i in issues if i.severity == "warning"]
    if warnings:
        client.logger.log(f"⚠️ Build proceeding with {len(warnings)} warnings", "warning")
    
    # Proceed with build
    client.compiler.compile()
    print("Build completed successfully.")


def check_command(args: argparse.Namespace) -> None:
    """Run comprehensive validation checks."""
    client = setup_client(args)
    checker = client.checker
    
    issues = checker.validate_all()
    
    if not issues:
        print("\n✨ All checks passed! Your invokers are healthy.\n")
        return
    
    # Group issues by severity
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    infos = [i for i in issues if i.severity == "info"]
    
    # Display issues
    if errors:
        print("\n❌ ERRORS:\n")
        for issue in errors:
            print(issue)
            print()
    
    if warnings:
        print("⚠️ WARNINGS:\n")
        for issue in warnings:
            print(issue)
            print()
    
    if infos:
        print("ℹ️ INFO:\n")
        for issue in infos:
            print(issue)
            print()
    
    # Summary
    print(f"\nSummary: {len(errors)} errors, {len(warnings)} warnings, {len(infos)} info\n")


def health_command(args: argparse.Namespace) -> None:
    """Check overall health of Sierra environment."""
    client = setup_client(args)
    checker = client.checker
    
    health = checker.health_check()
    
    # Display health status
    status_icon = {
        "healthy": "✅",
        "degraded": "⚠️",
        "unhealthy": "❌"
    }.get(health["status"], "❓")
    
    print(f"\n{status_icon} Health Status: {health['status'].upper()}\n")
    print(f"Invokers: {health['invokers_count']}")
    print(f"Errors: {health['issues']['errors']}")
    print(f"Warnings: {health['issues']['warnings']}\n")
    
    print("Environment Checks:")
    for check, status in health["checks"].items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {check.replace('_', ' ').title()}")
    
    print()


# ==================== Package Manager Commands ====================

def repo_add_command(args: argparse.Namespace) -> None:
    """Add a repository source."""
    config_dir = pathlib.Path.home() / ".sierra"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    repo_mgr = RepositoryManager(config_dir)
    
    try:
        source = repo_mgr.add_source(
            args.url,
            name=args.name,
            branch=args.branch,
            priority=args.priority
        )
        print(f"\n✅ Added repository: {source.name}")
        print(f"   URL: {source.url}")
        print(f"   Branch: {source.branch}\n")
        
        # Try to fetch registry
        print("🔍 Fetching package registry...")
        results = repo_mgr.update_registry(source.name)
        count = results.get(source.name, 0)
        
        if count > 0:
            print(f"✅ Found {count} packages\n")
        else:
            print("⚠️  Could not fetch registry (will retry on next update)\n")
            
    except Exception as e:
        print(f"❌ Error: {e}\n")
        sys.exit(1)


def repo_list_command(args: argparse.Namespace) -> None:
    """List all repository sources."""
    config_dir = pathlib.Path.home() / ".sierra"
    repo_mgr = RepositoryManager(config_dir)
    
    sources = repo_mgr.list_sources()
    
    if not sources:
        print("\n📦 No repositories configured.\n")
        print("Add a repository with: sierra repo add <url>\n")
        return
    
    print("\n📦 Configured Repositories:\n")
    
    for idx, source in enumerate(sources, 1):
        status_icon = "✅ enabled" if source.enabled else "❌ disabled"
        print(f"{idx}. {source.name} (priority: {source.priority}) {status_icon}")
        print(f"   URL: {source.url}")
        
        # Show package count if cached
        registry = repo_mgr.get_cached_registry(source.name)
        if registry:
            count = len(registry.get('packages', {}))
            cached_at = registry.get('_cached_at', 'unknown')
            print(f"   Packages: {count}")
            print(f"   Cached: {cached_at[:19]}")  # Show date without microseconds
        else:
            print(f"   Packages: Not cached yet")
        
        print()


def repo_update_command(args: argparse.Namespace) -> None:
    """Update package registries."""
    config_dir = pathlib.Path.home() / ".sierra"
    repo_mgr = RepositoryManager(config_dir)
    
    print("\n🔄 Updating repositories...\n")
    
    try:
        results = repo_mgr.update_registry(args.source)
        
        for source_name, count in results.items():
            if count > 0:
                print(f"✅ {source_name}: {count} packages")
            else:
                print(f"❌ {source_name}: Failed to update")
        
        print()
    except Exception as e:
        print(f"❌ Error: {e}\n")
        sys.exit(1)


def repo_remove_command(args: argparse.Namespace) -> None:
    """Remove a repository source."""
    config_dir = pathlib.Path.home() / ".sierra"
    repo_mgr = RepositoryManager(config_dir)
    
    if repo_mgr.remove_source(args.name):
        print(f"\n✅ Removed repository: {args.name}\n")
    else:
        print(f"\n❌ Repository '{args.name}' not found\n")
        sys.exit(1)


def search_command(args: argparse.Namespace) -> None:
    """Search for packages."""
    config_dir = pathlib.Path.home() / ".sierra"
    repo_mgr = RepositoryManager(config_dir)
    
    registry = PackageRegistry(repo_mgr)
    registry.refresh()
    
    search = PackageSearch(registry)
    
    filters = {}
    if args.tag:
        filters['tag'] = args.tag
    if args.category:
        filters['category'] = args.category
    if args.source:
        filters['source'] = args.source
    
    result = search.search_and_format(args.query, **filters)
    print(result)


def info_command(args: argparse.Namespace) -> None:
    """Show detailed package information."""
    config_dir = pathlib.Path.home() / ".sierra"
    repo_mgr = RepositoryManager(config_dir)
    
    registry = PackageRegistry(repo_mgr)
    registry.refresh()
    
    search = PackageSearch(registry)
    pkg = registry.get_package(args.package)
    
    if not pkg:
        print(f"\n❌ Package '{args.package}' not found\n")
        sys.exit(1)
    
    print(search.format_package_info(pkg, detailed=True))


def install_command(args: argparse.Namespace) -> None:
    """Install packages."""
    config_dir = pathlib.Path.home() / ".sierra"
    env_path = pathlib.Path.cwd() / (args.env if hasattr(args, 'env') else 'test_env')
    
    repo_mgr = RepositoryManager(config_dir)
    registry = PackageRegistry(repo_mgr)
    registry.refresh()
    
    installer = PackageInstaller(repo_mgr, env_path)
    
    packages = args.packages
    print(f"\n📦 Installing {len(packages)} package(s)...\n")
    
    success_count = 0
    for pkg_name in packages:
        try:
            print(f"{pkg_name}:")
            print(f"  ⬇️  Downloading...")
            installer.install(
                pkg_name, 
                registry, 
                force=args.force,
                skip_validation=args.skip_validation
            )
            print(f"  🔍 Validating..." if not args.skip_validation else "  ⚠️  Skipped validation")
            print(f"  ✅ Installed\n")
            success_count += 1
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
    
    print(f"✅ Successfully installed {success_count}/{len(packages)} packages")
    
    if success_count > 0:
        print("🔨 Run 'sierra build' to compile the new invokers\n")


def remove_command(args: argparse.Namespace) -> None:
    """Remove an installed package."""
    config_dir = pathlib.Path.home() / ".sierra"
    env_path = pathlib.Path.cwd() / (args.env if hasattr(args, 'env') else 'test_env')
    
    repo_mgr = RepositoryManager(config_dir)
    installer = PackageInstaller(repo_mgr, env_path)
    
    try:
        print(f"\n🗑️  Removing {args.package}...")
        installer.remove(args.package)
        print(f"✅ Removed successfully\n")
        print("🔨 Run 'sierra build' to rebuild\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
        sys.exit(1)


def list_command(args: argparse.Namespace) -> None:
    """List packages."""
    config_dir = pathlib.Path.home() / ".sierra"
    env_path = pathlib.Path.cwd() / (args.env if hasattr(args, 'env') else 'test_env')
    
    repo_mgr = RepositoryManager(config_dir)
    
    if args.installed:
        # List installed packages
        installer = PackageInstaller(repo_mgr, env_path)
        packages = installer.list_installed()
        
        if not packages:
            print("\n📦 No packages installed\n")
            return
        
        print(f"\n📦 Installed Packages ({len(packages)}):\n")
        for pkg in packages:
            print(f"{pkg['name']} v{pkg['version']}")
            print(f"  Installed: {pkg['installed_date'][:10]}")
            print(f"  Source: {pkg['source']}\n")
    
    else:
        # List available packages
        registry = PackageRegistry(repo_mgr)
        registry.refresh()
        
        packages_by_cat = registry.list_by_category()
        
        total = sum(len(pkgs) for pkgs in packages_by_cat.values())
        print(f"\n📦 Available Packages ({total} total):\n")
        
        for category, pkgs in sorted(packages_by_cat.items()):
            print(f"{category.upper()}:")
            for pkg in sorted(pkgs, key=lambda p: p.name):
                print(f"  {pkg.name} v{pkg.version}")
            print()


def upgradable_command(args: argparse.Namespace) -> None:
    """List packages with available updates."""
    config_dir = pathlib.Path.home() / ".sierra"
    env_path = pathlib.Path.cwd() / (args.env if hasattr(args, 'env') else 'test_env')
    
    repo_mgr = RepositoryManager(config_dir)
    registry = PackageRegistry(repo_mgr)
    installer = PackageInstaller(repo_mgr, env_path)
    
    updater = PackageUpdater(installer, registry)
    updates = updater.check_updates()
    
    if not updates:
        print("\n✅ All packages are up to date!\n")
        return
    
    print(f"\n📦 Upgradable Packages ({len(updates)}):\n")
    
    for update in updates:
        print(f"{update['name']}")
        print(f"  Installed: {update['current_version']}")
        print(f"  Available: {update['available_version']}")
        print(f"  Source: {update['source']}\n")
    
    print(f"Run 'sierra update --all' to upgrade all packages\n")


def update_command(args: argparse.Namespace) -> None:
    """Update installed packages."""
    config_dir = pathlib.Path.home() / ".sierra"
    env_path = pathlib.Path.cwd() / (args.env if hasattr(args, 'env') else 'test_env')
    
    repo_mgr = RepositoryManager(config_dir)
    registry = PackageRegistry(repo_mgr)
    installer = PackageInstaller(repo_mgr, env_path)
    
    updater = PackageUpdater(installer, registry)
    
    if args.all:
        # Update all packages
        print("\n🔄 Checking for updates...\n")
        updates = updater.check_updates()
        
        if not updates:
            print("✅ All packages are up to date!\n")
            return
        
        print(f"📦 Updating {len(updates)} package(s)...\n")
        
        results = updater.update_all()
        
        success_count = sum(1 for v in results.values() if v)
        print(f"\n✅ Successfully updated {success_count}/{len(results)} packages")
        
        if success_count > 0:
            print("🔨 Run 'sierra build' to rebuild with updated invokers\n")
    
    else:
        # Update specific package
        if not args.package:
            print("\n❌ Please specify a package name or use --all\n")
            sys.exit(1)
        
        try:
            print(f"\n🔄 Updating {args.package}...\n")
            updater.update_package(args.package)
            print(f"✅ Successfully updated {args.package}")
            print("🔨 Run 'sierra build' to rebuild\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
            sys.exit(1)


def setup_client(args: argparse.Namespace) -> typing.Any:
    """Setup Sierra client from arguments."""
    log_level = LogLevel.DEBUG if args.verbose else LogLevel.STANDARD
    
    client = sierra.SierraDevelopmentClient(
        environment_name=args.env,
        logger=UniversalLogger(
            name="Sierra",
            level=log_level,
        ),
    )
    client.load_invokers_from_scripts()
    return client


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="sierra-dev",
        description="Sierra Dev - Invoker Package Manager",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("name", nargs="?", default="default_env", help="Project name")
    init_parser.add_argument("--force", action="store_true", help="Force initialization")
    init_parser.set_defaults(func=init_command)

    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Clean generated files")
    clean_parser.add_argument("--env", default="default_env", help="Environment name")
    clean_parser.set_defaults(func=clean_command)

    # Build command
    build_parser = subparsers.add_parser("build", help="Build and compile invokers")
    build_parser.add_argument("--env", default="default_env", help="Environment name")
    build_parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    build_parser.set_defaults(func=build_command)
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Run validation checks")
    check_parser.add_argument("--env", default="default_env", help="Environment name")
    check_parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    check_parser.set_defaults(func=check_command)
    
    # Health command
    health_parser = subparsers.add_parser("health", help="Check environment health")
    health_parser.add_argument("--env", default="default_env", help="Environment name")
    health_parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    health_parser.set_defaults(func=health_command)
    
    # Repository commands
    repo_parser = subparsers.add_parser("repo", help="Manage package repositories")
    repo_subparsers = repo_parser.add_subparsers(dest="repo_command")
    
    # repo add
    repo_add = repo_subparsers.add_parser("add", help="Add a repository source")
    repo_add.add_argument("url", help="GitHub repository URL")
    repo_add.add_argument("--name", help="Custom name for source")
    repo_add.add_argument("--branch", default="main", help="Git branch")
    repo_add.add_argument("--priority", type=int, default=10, help="Source priority")
    repo_add.set_defaults(func=repo_add_command)
    
    # repo list
    repo_list = repo_subparsers.add_parser("list", help="List repositories")
    repo_list.set_defaults(func=repo_list_command)
    
    # repo update
    repo_update = repo_subparsers.add_parser("update", help="Update package registries")
    repo_update.add_argument("source", nargs="?", help="Specific source to update")
    repo_update.set_defaults(func=repo_update_command)
    
    # repo remove
    repo_remove = repo_subparsers.add_parser("remove", help="Remove a repository")
    repo_remove.add_argument("name", help="Repository name")
    repo_remove.set_defaults(func=repo_remove_command)
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for packages")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--tag", help="Filter by tag")
    search_parser.add_argument("--category", help="Filter by category")
    search_parser.add_argument("--source", help="Filter by source")
    search_parser.set_defaults(func=search_command)
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show package information")
    info_parser.add_argument("package", help="Package name")
    info_parser.set_defaults(func=info_command)
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install packages")
    install_parser.add_argument("packages", nargs="+", help="Package(s) to install")
    install_parser.add_argument("--env", default="test_env", help="Target environment")
    install_parser.add_argument("--force", action="store_true", help="Force reinstall")
    install_parser.add_argument("--skip-validation", action="store_true", help="Skip type safety validation")
    install_parser.set_defaults(func=install_command)
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update packages")
    update_parser.add_argument("package", nargs="?", help="Package to update")
    update_parser.add_argument("--all", action="store_true", help="Update all packages")
    update_parser.add_argument("--env", default="test_env", help="Target environment")
    update_parser.set_defaults(func=update_command)
    
    # Upgradable command
    upgradable_parser = subparsers.add_parser("upgradable", help="List upgradable packages")
    upgradable_parser.add_argument("--env", default="test_env", help="Target environment")
    upgradable_parser.set_defaults(func=upgradable_command)
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a package")
    remove_parser.add_argument("package", help="Package to remove")
    remove_parser.add_argument("--env", default="test_env", help="Target environment")
    remove_parser.set_defaults(func=remove_command)
    
    # List command
    list_parser = subparsers.add_parser("list", help="List packages")
    list_parser.add_argument("--installed", action="store_true", help="Show installed packages")
    list_parser.add_argument("--env", default="test_env", help="Target environment")
    list_parser.set_defaults(func=list_command)
    
    args = parser.parse_args()
    
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
