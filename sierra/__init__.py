import typing


def create_tree_result(
    results: list[typing.Union[str, dict[str, list[str]]]],
) -> dict[str, str]:
    """
    Create a Tree type result.

    Parameters
    ----------
    results : list[Union[str, dict[str, list[str]]]]
        The tree results.

    Returns
    -------
    TreeResult
        The formatted tree result.
    """
    result: dict[str, typing.Any] = {
        "type": "Tree",
        "results": results,
    }
    return result


def create_network_result(
    origins: list[str],
    nodes: list[dict[str, str]],
    edges: list[dict[str, str]],
) -> dict[str, str]:
    """
    Create a Network type result.

    Parameters
    ----------
    origins : list[str]
        List of origin node IDs.
    nodes : list[dict[str, str]]
        List of node definitions.
    edges : list[dict[str, str]]
        List of edge definitions.

    Returns
    -------
    NetworkResult
        The formatted network result.
    """
    result: dict[str, typing.Any] = {
        "type": "Network",
        "origins": origins,
        "nodes": nodes,
        "edges": edges,
    }
    return result


def create_error_result(message: str) -> dict[str, str]:
    """
    Create an Error type result.

    Parameters
    ----------
    message : str
        The error message.

    Returns
    -------
    ErrorResult
        The formatted error result.
    """
    result: dict[str, typing.Any] = {
        "type": "Error",
        "message": message,
    }

    return result
