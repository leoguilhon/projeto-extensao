import re

from fastapi import HTTPException, status


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_text(value: str, *, collapse_internal_whitespace: bool = True) -> str:
    normalized = value.strip()
    if collapse_internal_whitespace:
        normalized = " ".join(normalized.split())
    return normalized


def validate_required_text(
    value: str,
    field_label: str,
    *,
    min_length: int,
    max_length: int,
    collapse_internal_whitespace: bool = True,
) -> str:
    normalized = normalize_text(value, collapse_internal_whitespace=collapse_internal_whitespace)
    if len(normalized) < min_length:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"{field_label} deve ter pelo menos {min_length} caracteres desconsiderando espacos.",
        )
    if len(normalized) > max_length:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"{field_label} deve ter no maximo {max_length} caracteres.",
        )
    return normalized


def validate_optional_text(
    value: str,
    field_label: str,
    *,
    max_length: int,
    collapse_internal_whitespace: bool = True,
) -> str:
    normalized = normalize_text(value, collapse_internal_whitespace=collapse_internal_whitespace)
    if len(normalized) > max_length:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"{field_label} deve ter no maximo {max_length} caracteres.",
        )
    return normalized


def normalize_email(email: str) -> str:
    normalized = email.strip().lower()
    if not EMAIL_PATTERN.fullmatch(normalized):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Informe um e-mail valido.",
        )
    return normalized
