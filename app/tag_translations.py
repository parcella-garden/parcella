"""
Per-language names for the free-form tags (MemberTag, ExternalContactTag;
ADR 0098). A tag keeps the name it was typed with; `translations` maps a
language code to the name shown while the club runs in that language
("Rote Liste" -> {"en": "red flag"}). Shared by both tag pools so the
two can't drift apart.
"""
from typing import Optional, Protocol, Sequence

from jinja2 import pass_context

from app.i18n import AVAILABLE_LANGUAGES, DEFAULT_LANGUAGE
from app.services.errors import ServiceError


class _Tag(Protocol):
    id: str
    name: str
    translations: Optional[dict]


def tag_label(tag: _Tag, lang: str) -> str:
    """The tag's name in `lang`, or the name it was typed with."""
    return (tag.translations or {}).get(lang) or tag.name


@pass_context
def jinja_tag_name(context, tag: _Tag) -> str:
    """Jinja global `tag_name(tag)` -- uses the request's language, like `t`."""
    request = context.get("request")
    lang = getattr(request.state, "language", DEFAULT_LANGUAGE) if request else DEFAULT_LANGUAGE
    return tag_label(tag, lang)


def all_names(tag: _Tag) -> set[str]:
    """Base name and every translation, lowercased."""
    return {tag.name.lower(), *(v.lower() for v in (tag.translations or {}).values())}


def find_tag_by_name(tags: Sequence[_Tag], name: str) -> Optional[_Tag]:
    """A tag whose name or any translation equals `name`, ignoring case --
    so typing "red flag" in an English UI reuses "Rote Liste" instead of
    creating a second tag. A base-name match wins over a translation."""
    wanted = name.lower()
    for tag in tags:
        if tag.name.lower() == wanted:
            return tag
    for tag in tags:
        if wanted in all_names(tag):
            return tag
    return None


def clean_translations(
    tag: _Tag, values: dict, others: Sequence[_Tag], *, max_length: int, error_prefix: str,
) -> dict:
    """Validated {lang: name} for `tag`: known languages only, whitespace
    collapsed, empties dropped, and no name another tag already uses
    (as name or translation) -- that would make typed names ambiguous."""
    cleaned = {}
    for lang in AVAILABLE_LANGUAGES:
        value = " ".join((values.get(lang) or "").split())
        if not value:
            continue
        if len(value) > max_length:
            raise ServiceError(f"{error_prefix}.name_too_long", max=max_length)
        clash = find_tag_by_name([o for o in others if o.id != tag.id], value)
        if clash is not None:
            raise ServiceError(f"{error_prefix}.name_taken", http_status=409, name=clash.name)
        cleaned[lang] = value
    return cleaned
