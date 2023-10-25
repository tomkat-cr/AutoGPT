# poetry add PyPDF2
from __future__ import annotations
import json

from PyPDF2 import PdfReader, PdfWriter
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyPDFLoader

from ..registry import ability


def get_pdf_pages(pdf_docs: list) -> list:
    all_pages = []
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        pdf_writer = PdfWriter()

        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

        with open(pdf.name, 'wb') as output_file:
            pdf_writer.write(output_file)
        text_splitter = CharacterTextSplitter(
            separator="\n\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        loader = PyPDFLoader(pdf.name)
        pdf_pages = loader.load_and_split(text_splitter=text_splitter)
        all_pages += pdf_pages
    return all_pages


@ability(
    name="pdf_load",
    description="Read all PDF files content",
    parameters=[
        {
            "name": "pdf_files",
            "description": "List of PDF files to load",
            "type": "list[str]",
            "required": True,
        },
    ],
    output_type="list[str]",
)
async def pdf_load(agent, task_id: str, pdf_files: list[str]) -> str:
    """Return all PDF files content

    Args:
        pdf_files (lst[str]): List of PDF files to load.

    Returns:
        str: content of all PDF files.
    """
    results = json.dumps(
        get_pdf_pages(pdf_files),
        ensure_ascii=False,
        indent=4
    )
    return results
