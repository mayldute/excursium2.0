def validate_individual_client(user: dict, legal_type: str | None) -> None:
    """Validate fields for an individual client.

    Args:
        user (dict): Dictionary containing user data (e.g., first_name, last_name, phone_number).
        legal_type (Optional[str]): The legal type of the client, expected to be None for individual clients.

    Returns:
        None

    Raises:
        ValueError: If required user fields are missing or legal_type is not None.
    """
    # Check required user fields
    required_user_fields = ['first_name', 'last_name', 'phone_number']
    missing = [f for f in required_user_fields if not user.get(f)]
    if missing:
        raise ValueError(f"Missing fields for individual client: {missing}")

    # Validate legal type
    if legal_type is not None:
        raise ValueError("Legal type must be empty for individual clients.")


def validate_legal_minimal(values: dict) -> None:
    """Validate minimal required fields for a legal entity during registration.

    Args:
        values (dict): Dictionary containing legal entity data (e.g., company_name, inn, kpp, legal_type).

    Returns:
        None

    Raises:
        ValueError: If required fields are missing, INN/KPP lengths are invalid, or custom_type is missing for 'OTH' legal type.
    """
    # Check required fields
    required_fields = ["company_name", "inn", "kpp", "legal_type"]
    missing = [f for f in required_fields if not values.get(f)]
    if missing:
        raise ValueError(f"Missing fields for legal entity: {missing}")

    # Validate INN and KPP lengths
    legal_type = values["legal_type"]
    custom_type = values.get("custom_type")
    if legal_type == "OTH" and not custom_type:
        raise ValueError("Custom type is required when legal_type is 'OTH'.")
    
    # Validate INN length
    inn = values.get("inn", "")
    if legal_type == "IE" and len(inn) != 12:
        raise ValueError("INN must be 12 characters for IE.")
    elif legal_type != "IE" and len(inn) != 10:
        raise ValueError("INN must be 10 characters for other legal types.")

    # Validate KPP length
    kpp = values.get("kpp", "")
    if len(kpp) != 9:
        raise ValueError("KPP must be 9 characters long.")


def validate_legal_entity(values: dict) -> None:
    """Validate fields for a legal entity, including extended fields like OGRN and bank accounts.

    Args:
        values (dict): Dictionary containing legal entity data (e.g., legal_type, inn, kpp, ogrn, bank details).

    Returns:
        None

    Raises:
        ValueError: If fields have invalid lengths, formats, or values (e.g., missing custom_type for 'OTH', invalid account formats).
    """
    # Validate legal type and custom type
    legal_type = values.get("legal_type")
    custom_type = values.get("custom_type")

    if legal_type == "OTH" and not custom_type:
        raise ValueError("Custom type is required when legal_type is 'OTH'.")

    def check_length(field_value, expected_len, field_name)-> None:
        """Check if a field value has the expected length, if provided.

        Args:
            field_value (Optional[str]): The value to check.
            expected_len (int): The expected length of the field.
            field_name (str): The name of the field for error messages.

        Raises:
            ValueError: If the field value is provided and does not match the expected length.
        """
        if field_value and len(field_value) != expected_len:
            raise ValueError(f"{field_name} must be {expected_len} characters long.")

    # Validate INN length
    inn = values.get("inn")
    if inn:
        if legal_type == "IE":
            check_length(inn, 12, "INN")
        else:
            check_length(inn, 10, "INN")

    # Validate other required fields
    check_length(values.get("kpp"), 9, "KPP")
    check_length(values.get("ogrn"), 13, "OGRN")
    check_length(values.get("current_account"), 20, "Current account")
    check_length(values.get("bik"), 9, "BIK")

    # Validate correspondent account
    corresp_account = values.get("corresp_account")
    bik = values.get("bik")
    
    if corresp_account:
        check_length(corresp_account, 20, "Correspondent account")
        if not corresp_account.startswith("30101"):
            raise ValueError("Correspondent account must start with '30101'.")
        if bik and corresp_account[-3:] != bik[-3:]:
            raise ValueError("Last 3 digits of correspondent account must match BIK.")

    # Validate OKTMO
    oktmo = values.get("oktmo")
    if oktmo and len(oktmo) not in [8, 11]:
        raise ValueError("OKTMO must be 8 or 11 characters long.")