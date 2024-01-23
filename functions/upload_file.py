from flask import request, jsonify
import os
import fitz  # PyMuPDF


def upload_file():
    print('FILES', request.files)
    uploaded_files = request.files.getlist('files')
    if not uploaded_files:
        return jsonify({'error': 'No files provided'})

    text_content_by_file = []

    for file in uploaded_files:
        if file.filename == '':
            return jsonify({'error': 'One or more selected files have no name'})

        if file:
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)

            try:
                if file.filename.lower().endswith(('.pdf', '.doc', '.docx')):
                    pages = extract_text_with_properties(file_path)
                else:
                    return jsonify({'error': 'Unsupported file format'})

                text_content_by_file.append({'filename': file.filename, 'text_content': pages})
                os.remove(file_path)

            except Exception as e:
                return jsonify({'error': f'Error processing file {file.filename}: {str(e)}'})

    return jsonify({'files': text_content_by_file})

# Define a custom sorting key


def extract_text_with_properties(pdf_path):
    doc = fitz.open(pdf_path)
    text_with_properties_by_page = []

    for page_num in range(doc.page_count):
        page = doc[page_num]
        blocks = page.get_text("dict", flags=11)["blocks"]
        text_with_properties = []

        for b in blocks:  # iterate through the text blocks
            for l in b["lines"]:  # iterate through the text lines
                for s in l["spans"]:  # iterate through the text spans
                    text_with_properties.append({
                        "text": s["text"],
                        "page": page_num+1,
                        "color": "#%06x" % s["color"],
                        "font_style": flags_decomposer(s["flags"]),
                        "x": s["origin"][0],
                        "y": s["origin"][1],
                    })
        text_with_properties_by_page.append(
            sorted(text_with_properties, key=lambda x: x['y']))

    doc.close()
    return text_with_properties_by_page


def extract_words_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    words = []
    pagesResult = []
    for page_num in range(doc.page_count):
        page = doc[page_num]
        page_words = page.get_text("words")
        pagesResult.append(page_words)
        for word_info in page_words:
            # Text content is at index 4 in the word information
            word = word_info[4]
            words.append(word)

    doc.close()
    return pagesResult


def sort_by_page(item):
    return (item['page'])


def sort_by_y(item):
    return (item['y'])


def extract_text_with_style_and_coordinates(pdf_path):
    doc = fitz.open(pdf_path)
    text_with_properties = []
    for page_num in range(doc.page_count):
        page = doc[page_num]
        words = page.get_text("words")
        for word_info in words:
            word_text = word_info[4]
            x, y = word_info[0], word_info[1]
            font_size = word_info[3]
            font_name = word_info[6]
            font_color = word_info[7]
            text_with_properties.append({
                "text": word_text,
                "page": page_num+1,
                "color": font_color,
                # "font_style": flags_decomposer(s["flags"]),
                "x": x,  # add x coordinate
                "y": y,  # add y coordinate
            })
    doc.close()
    return text_with_properties


def flags_decomposer(flags):
    flag_descriptions = {
        1: "Superscript",
        2: "Subscript",
        3: "Italic",
        4: "Underline",
        5: "Strikeout",
        6: "Overlined",
        7: "Small caps",
        8: "Bold",
        9: "Serif",
        10: "Script",
        11: "Italic (angled)",
        12: "All caps",
        # Add more flag descriptions as needed based on your flags
    }

    decomposed_flags = [flag_descriptions.get(bit, f"Unknown Flag {bit}")
                        for bit in range(32) if flags & (1 << bit)]

    return ", ".join(decomposed_flags)


def extract_text_by_color(pdf_path):
    doc = fitz.open(pdf_path)
    target_color = "#fb0106"
    result_data = []

    for page_num in range(doc.page_count):
        page = doc[page_num]
        text_blocks = page.get_text("dict", flags=11)["blocks"]
        for block in text_blocks:
            for line in block["lines"]:
                for span in line["spans"]:
                    # Color is at index 6 in the span information
                    color = "#%06x" % span["color"]
                    # Check if the color matches the target color (0xFF0000 for red)
                    # if color == target_color:
                    # Text content is at index 4 in the span information
                    text = span["text"]
                    # X and Y coordinates
                    x, y = span["origin"][0], span["origin"][1]

                    result_data.append({
                        "text": text,
                        "color": color,
                        "x": x,
                        "y": y,
                        "page": page_num + 1  # Adjust page number to start from 1
                    })

    doc.close()
    return result_data
