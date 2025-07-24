import phonenumbers

import sierra

invoker = sierra.InvokerScript(
    name="analyze-phone-number",
    description="Extracts offline metadata from a phone number using libphonenumber.",
)

invoker.requirement(["phonenumbers"])


@invoker.dependancy
def extract_info(number: str) -> dict[str, str]:
    info: dict[str, str] = {}
    try:
        parsed = phonenumbers.parse(number, None)
    except phonenumbers.NumberParseException as e:
        return {"error": f"Invalid number format: {e!s}"}

    info["International"] = phonenumbers.format_number(
        parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
    )
    info["E.164"] = phonenumbers.format_number(
        parsed, phonenumbers.PhoneNumberFormat.E164
    )
    info["National"] = phonenumbers.format_number(
        parsed, phonenumbers.PhoneNumberFormat.NATIONAL
    )
    info["Country Code"] = str(parsed.country_code)
    info["Region"] = phonenumbers.region_code_for_number(parsed) or "Unknown"
    info["Valid"] = str(phonenumbers.is_valid_number(parsed))
    info["Possible"] = str(phonenumbers.is_possible_number(parsed))

    typ = phonenumbers.number_type(parsed)
    typ_str = {
        phonenumbers.PhoneNumberType.MOBILE: "Mobile",
        phonenumbers.PhoneNumberType.FIXED_LINE: "Fixed Line",
        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed or Mobile",
        phonenumbers.PhoneNumberType.TOLL_FREE: "Toll Free",
        phonenumbers.PhoneNumberType.PREMIUM_RATE: "Premium Rate",
        phonenumbers.PhoneNumberType.SHARED_COST: "Shared Cost",
        phonenumbers.PhoneNumberType.VOIP: "VoIP",
        phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
        phonenumbers.PhoneNumberType.PAGER: "Pager",
        phonenumbers.PhoneNumberType.UAN: "UAN",
        phonenumbers.PhoneNumberType.VOICEMAIL: "Voicemail",
        phonenumbers.PhoneNumberType.UNKNOWN: "Unknown",
    }.get(typ, "Unknown")
    info["Type"] = typ_str

    return info


@invoker.entry_point
def run(
    phone: sierra.Param[
        str | None,
        sierra.SierraOption(
            description="Phone number in international format (e.g. +919876543210)",
            mandatory="MANDATORY",
        ),
    ],
) -> None:
    if not phone:
        result = sierra.create_error_result("No phone number provided.")
    else:
        data = extract_info(phone)
        if "error" in data:
            result = sierra.create_error_result(data["error"])
        else:
            # Fix the type issue by creating a list of str | dict[str, list[str]]
            tree_data: list[str | dict[str, list[str]]] = ["### Phone Info"]
            for k, v in data.items():
                tree_data.append({k: [v]})
            result = sierra.create_tree_result(tree_data)
    print(result)


def load(client: sierra.SierraDevelopmentClient) -> None:
    client.load_invoker(invoker)
