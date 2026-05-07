import os
from flask import Blueprint, request, jsonify
from flask_login import login_required
from groq import Groq

ai = Blueprint('ai', __name__, url_prefix='/api/v1/ai')

_client = None

def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
    return _client


@ai.route('/book_chat', methods=['POST'])
@login_required
def book_chat():
    payload = request.get_json()
    book = payload.get('book', {})
    messages = payload.get('messages', [])

    title = book.get('title', 'Unknown')
    authors = book.get('authors', '')
    description = book.get('description', '')
    isbn = book.get('isbn', '')
    subject = book.get('subject', '')
    price = book.get('price', '')

    book_context = f"Title: {title}"
    if authors:
        book_context += f"\nAuthor(s): {authors}"
    if subject:
        book_context += f"\nSubject: {subject}"
    if isbn:
        book_context += f"\nISBN: {isbn}"
    if price:
        book_context += f"\nPrice: ${price}"
    if description:
        book_context += f"\nDescription/Excerpt: {description}"

    system_prompt = (
        "You are a knowledgeable book assistant helping a student on UConnect, a college textbook marketplace. "
        "Answer questions about the following book concisely and helpfully. "
        "If asked for a summary, give a 2-3 sentence overview of what the book covers. "
        "If the user asks whether they need this book for a course, give honest practical advice. "
        "Keep all responses under 150 words unless a longer answer is clearly needed.\n\n"
        f"Book information:\n{book_context}"
    )

    groq_messages = [
        {'role': m['role'], 'content': m['content']}
        for m in messages
        if m.get('role') in ('user', 'assistant') and m.get('content')
    ]

    try:
        response = get_client().chat.completions.create(
            model='llama-3.1-8b-instant',
            max_tokens=400,
            messages=[{'role': 'system', 'content': system_prompt}] + groq_messages,
        )
        reply = response.choices[0].message.content
        return jsonify({'data': {'reply': reply}}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
