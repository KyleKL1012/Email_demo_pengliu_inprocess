import unicodedata
from bs4 import BeautifulSoup

import re




def remove_html_tags(text: str) -> str:
    """Remove html tags.

    Args:
        text (str): The text string.

    Returns:
        (str): Cleaned text.

    """
    soup = BeautifulSoup(text)
    return soup.get_text()

def unicode_text(text: str) -> str:
    """Encode the text to avoid strange characters.

    Args:
        text (str): The text.

    Returns:
        (str): Encoded text.

    """
    return unicodedata.normalize("NFKD", text)

def whitespace_normalization(text: str) -> str:
    """Normalize whitespace

    Args:
        text (str): The text.

    Returns:
        (str): Encoded text.

    """
    text = text.strip()
    
    text = re.sub(r'\s+', ' ', text)
    
    text = text.replace('\t', ' ')
    
    text = text.replace('\n', ' ')
    
    return text

import re

def remove_hyperlinks(text: str) -> str:
    """Remove hyperlinks.

    Args:
        text (str): The text.

    Returns:
        (str): Encoded text without hyperlinks.
    """
    pattern = r"\[(.*?)\]\((.*?)\)"
    
    text = re.sub(pattern, r"\1", text)
    
    return text

# def clean_empty_lines(text: str, headlines: List[Dict]) -> Tuple[str, List[Dict]]:
        
#         if headlines:
#             num_headlines = len(headlines)
#             multiple_new_line_matches = re.finditer(r"\n\n\n+", text)
#             cur_headline_idx = 0
#             num_removed_chars_accumulated = 0
#             for match in multiple_new_line_matches:
#                 num_removed_chars_current = match.end() - match.start() - 2
#                 for headline_idx in range(cur_headline_idx, num_headlines):
#                     if match.end() - num_removed_chars_accumulated <= headlines[headline_idx]["start_idx"]:
#                         headlines[headline_idx]["start_idx"] -= num_removed_chars_current
#                     else:
#                         cur_headline_idx += 1
#                 num_removed_chars_accumulated += num_removed_chars_current

#         cleaned_text = re.sub(r"\n\n\n+", "\n\n", text)
#         return cleaned_text, headlines

# def find_and_remove_header_footer(
#         self, text: str, n_chars: int, n_first_pages_to_ignore: int, n_last_pages_to_ignore: int
#     ) -> str:
#         """
#         Heuristic to find footers and headers across different pages by searching for the longest common string.
#         For headers we only search in the first n_chars characters (for footer: last n_chars).
#         Note: This heuristic uses exact matches and therefore works well for footers like "Copyright 2019 by XXX",
#          but won't detect "Page 3 of 4" or similar.

#         :param n_chars: number of first/last characters where the header/footer shall be searched in
#         :param n_first_pages_to_ignore: number of first pages to ignore (e.g. TOCs often don't contain footer/header)
#         :param n_last_pages_to_ignore: number of last pages to ignore
#         :return: (cleaned pages, found_header_str, found_footer_str)
#         """

#         pages = text.split("\f")

#         # header
#         start_of_pages = [p[:n_chars] for p in pages[n_first_pages_to_ignore:-n_last_pages_to_ignore]]
#         found_header = self._find_longest_common_ngram(start_of_pages)
#         if found_header:
#             pages = [page.replace(found_header, "") for page in pages]

#         # footer
#         end_of_pages = [p[-n_chars:] for p in pages[n_first_pages_to_ignore:-n_last_pages_to_ignore]]
#         found_footer = self._find_longest_common_ngram(end_of_pages)
#         if found_footer:
#             pages = [page.replace(found_footer, "") for page in pages]
#         logger.debug("Removed header '%s' and footer '%s' in document", found_header, found_footer)
#         text = "\f".join(pages)
#         return text