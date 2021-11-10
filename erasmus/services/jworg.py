import re
from typing import Final

from attr import attrib, dataclass
from bs4 import BeautifulSoup
from yarl import URL

from ..data import Passage, SearchResults, VerseRange
from ..exceptions import BibleNotSupportedError
from ..json import loads
from ..protocols import Bible
from .base_service import BaseService

BOOKS: Final[tuple[str]] = (
    # first one avoid the 0 indexes, and shifts all other books names to have a
    # 1-based index.
    None,
    'Genesis',
    'Exodus',
    'Leviticus',
    'Numbers',
    'Deuteronomy',
    'Joshua',
    'Judges',
    'Ruth',
    '1 Samuel',
    '2 Samuel',
    '1 Kings',
    '2 Kings',
    '1 Chronicles',
    '2 Chronicles',
    'Ezra',
    'Nehemiah',
    'Esther',
    'Job',
    'Psalm',
    'Proverbs',
    'Ecclesiastes',
    'Song of Solomon',
    'Isaiah',
    'Jeremiah',
    'Lamentations',
    'Ezekiel',
    'Daniel',
    'Hosea',
    'Joel',
    'Amos',
    'Obadiah',
    'Jonah',
    'Micah',
    'Nahum',
    'Habakkuk',
    'Zephaniah',
    'Haggai',
    'Zechariah',
    'Malachi',
    'Matthew',
    'Mark',
    'Luke',
    'John',
    'Acts',
    'Romans',
    '1 Corinthians',
    '2 Corinthians',
    'Galatians',
    'Ephesians',
    'Philippians',
    'Colossians',
    '1 Thessalonians',
    '2 Thessalonians',
    '1 Timothy',
    '2 Timothy',
    'Titus',
    'Philemon',
    'Hebrews',
    'James',
    '1 Peter',
    '2 Peter',
    '1 John',
    '2 John',
    '3 John',
    'Jude',
    'Revelation',
)


@dataclass(slots=True)
class JWOrg(BaseService):
    _chap_url: URL = attrib(init=False)

    def __attrs_post_init__(self, /) -> None:
        self._chap_url = "https://wol.jw.org/{version}/{book_num}/{chap_num}"

    async def get_passage(self, bible: Bible, verses: VerseRange, /) -> Passage:
        book_num = BOOKS.index(verses.book)
        chap_num = verses.start.chapter

        async with self.session.get(
            self._chap_url.format(
                version=bible.service_version,
                book_num=book_num,
                chap_num=chap_num,
            ),
            # resets User-Agent to make requests faster. it seems that the
            # website detects programmatic clients and halts their requests on
            # porpuse.
            headers={"User-Agent": ""},
        ) as resp:
            # TODO: deal with 404
            soup = BeautifulSoup(await resp.read(), "html.parser")

            verse_texts = []
            for span in soup.findAll("span", id=self._verse_id_matcher(verses)):
                # it means it's the first verse of the chapter
                if span.strong:
                    span.strong.string = span.strong.string.strip()
                    span.strong.insert_before("__BOLD__")
                    span.strong.insert_after(".__BOLD__")
                # regular verses have a <a> tag to identify its number
                elif span.a:
                    # cleans peripheral whitespaces
                    span.a.string = span.a.string.strip()
                    span.a.insert_before("__BOLD__")
                    span.a.insert_after(".__BOLD__ ")
                verse_texts.append(span.get_text(''))

            return Passage(
                text=self.replace_special_escapes(
                    bible,
                    self._clean_text(' '.join(verse_texts)),
                ),
                range=verses,
                version=bible.abbr,
            )

    async def search(
        self, bible: Bible, terms: list[str], /, *, limit: int = 20, offset: int = 0
    ) -> SearchResults:
        raise BibleNotSupportedError(bible.abbr)

    def _verse_id_matcher(self, verses: VerseRange):
        book_num = BOOKS.index(verses.book)
        verse_nums = map(
            str,
            range(verses.start.verse, (verses.end or verses.start).verse + 1),
        )
        # only lists verses within a single chapter, for now
        chap_num = verses.start.chapter
        verse_id_re = re.compile(
            rf"v{book_num}-{chap_num}-({'|'.join(verse_nums)})-\d+"
        )

        def matcher(id):
            return id and verse_id_re.match(id)

        return matcher

    def _clean_text(self, text: str) -> str:
        return text.replace("*", "").replace("+", "")
