import streamlit as st
from PIL import Image
import numpy as np
import base64
import io
import tempfile
from pdf2image import convert_from_bytes
import cv2
import pytesseract
from table_detection import table_detection_boxes

st.set_page_config(
    page_title="StreamlineScanX",
    page_icon=":computer:",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://www.linkedin.com/in/arpitsinghgautam/',
        'Report a bug': "https://github.com/arpitsinghgautam/StreamlineScanX-ArizonaHacks/issues",
        'About': " StreamlineScanX is an advanced document OCR and analysis tool designed to streamline your document processing workflow. It leverages the power of Pytesseract, a popular OCR library, to extract text from images and PDFs. With StreamlineScanX, you can easily digitize your documents, extract valuable information, and gain insights from the text data"
    }
)


def main():
        image_file = 'assets/sidebar.jpg'
        with open(image_file, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        st.markdown(
            f"""
            <style>
            .css-6qob1r {{
                background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
                background-size: cover;
                colour:
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
        st.sidebar.title('StreamlineScanX')
        st.sidebar.write('Free Online OCR Tool')
        main_page_button = st.sidebar.button("Main Page")
        how_to_use_button = st.sidebar.button("How to use")
        about_button = st.sidebar.button("About StreamlineScanX")
        

        st.sidebar.write('StreamlineScanX is a powerful document OCR and analysis tool that simplifies document processing, allowing you to upload PNG images or PDF files to extract text, detect tables, and gain valuable insights with ease.')
        # Default homepage
        show_main_page = True  # Flag variable

        if main_page_button:
            show_main_page = False
            mainpage()
        elif how_to_use_button:
            show_main_page = False
            how_to_use()
        elif about_button:
            show_main_page = False
            show_about_streamlineScanX()

        if show_main_page:
            mainpage()
# Function to load and preprocess the uploaded image
def load_image(image_file):
    img = Image.open(image_file)
    return img


# Function to perform OCR on the image
def perform_ocr(image):
    image_np = np.array(image)

    # Perform OCR using Pytesseract with output as data
    result = pytesseract.image_to_data(image_np, lang='eng', output_type=pytesseract.Output.DICT)
    # Process each word region in the result
    table = table_detection_boxes(image_np)
    for box in table:
        xmin, ymin, xmax, ymax = box
        cv2.rectangle(image_np, (xmin, ymin), (xmax, ymax), (255, 0, 0), 2)
    
    for i in range(len(result['text'])):
        word = result['text'][i]
        conf = int(result['conf'][i])
        (x, y, w, h) = (result['left'][i], result['top'][i], result['width'][i], result['height'][i])

        # Filter out low confidence words
        if conf > 20:
            skip_box = False
            for table_box in table:
                table_xmin, table_ymin, table_xmax, table_ymax = table_box
                if x > table_xmin and x + w < table_xmax and y > table_ymin and y + h < table_ymax:
                    skip_box = True
                    break
            
            if not skip_box:
                # Draw the bounding box rectangle
                cv2.rectangle(image_np, (x, y), (x + w, y + h), (0, 255, 0), 1)
    
    ocr_text = pytesseract.image_to_string(image, lang='eng') # Specify the language(s) for OCR
    return ocr_text, image_np


# Function to process PDF files
def process_pdf(uploaded_file, flag):
    pdf_file = io.BytesIO(uploaded_file.read())
    pdf_pages = convert_from_bytes(pdf_file.getbuffer())
    
    pdf_text = ""
    images = []

    if flag == 1:
        for page_num, page in enumerate(pdf_pages):
            image = np.array(page)
            image_pil = Image.fromarray(image)
            ocr_text, img = perform_ocr(image_pil)
            st.image(img, caption=f"OCR of Page {page_num+1} Completed", use_column_width=True)
            pdf_text += ocr_text + "\n\n"
        
        return pdf_text.strip()
    
    elif flag == 2:
        for page_num, page in enumerate(pdf_pages):
            image = np.array(page)
            image_pil = Image.fromarray(image)
            images.append(image_pil)
        
        return images


# Streamlit app
def mainpage():
    mainpage_image_file = 'assets/mainpage.jpg'
    with open(mainpage_image_file, "rb") as mainpage_image_file:
        mainpage_encoded_string = base64.b64encode(mainpage_image_file.read())
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/{"png"};base64,{mainpage_encoded_string.decode()});
            background-size: cover
        }}
        </style>
        """,
        unsafe_allow_html=True
        )
    st.image('assets\StreamlineScanX-logo-big-curved.png', use_column_width=True)
    st.title("Document OCR and Analysis")
    # File upload and OCR
    uploaded_file = st.file_uploader("Upload a document as PNG or PDF", type=["png", "pdf"])
    if uploaded_file is not None:
        if uploaded_file.type == "image/png":
            image = load_image(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            st.write("")
            st.write("Running OCR...")
            ocr_text, img = perform_ocr(image)
            st.image(img, caption="Image with Bounding Boxes", use_column_width=True)
            st.write("OCR Text:")
            st.write(ocr_text)
        elif uploaded_file.type == "application/pdf":
            app_section = st.selectbox('Go to', ['Select a option:','Complete Text of the PDF', 'Each Page Text with Image'])
            if app_section == 'Select a option:':
                return
            elif app_section == 'Complete Text of the PDF':
                ocr_text = process_pdf(uploaded_file, 1)
                st.write("Running OCR...")
                st.write("PDF Text:")
                st.write(ocr_text)
            elif app_section == 'Each Page Text with Image':
                images = process_pdf(uploaded_file, 2)
                if images:
                    st.write(f"Total no. of Pages: {len(images)}")
                    for i, image in enumerate(images):
                        st.write("")
                        st.write("Running OCR on Image...")
                        ocr_text, img = perform_ocr(image)
                        st.image(img, caption=f"Page {i+1} with Bounding Boxes", use_column_width=True)
                        st.write("OCR Text:")
                        st.write(ocr_text)
        else:
            st.error("Invalid file format. Please upload a PNG image or a PDF file.")

        # Download extracted text as TXT
        def save_text_to_file(text):
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
            temp_file.write(text)
            temp_file.close()
            with open(temp_file.name, 'r') as file:
                file_data = file.read()
            return file_data
        
        txt_download = save_text_to_file(ocr_text)
        st.download_button(
            "Download Extracted Text",
            data=txt_download,
            file_name="extracted_text.txt",
            mime="text/plain"
        )

    st.write("---")
    st.write("Note: OCR accuracy may vary depending on the document quality and content.")



def how_to_use():
    how_to_use_image_file = 'assets/howtouse.jpg'
    with open(how_to_use_image_file, "rb") as how_to_use_image_file:
        how_to_use_encoded_string = base64.b64encode(how_to_use_image_file.read())
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/{"png"};base64,{how_to_use_encoded_string.decode()});
            background-size: cover
        }}
        </style>
        """,
        unsafe_allow_html=True
        )
    st.title("How to use StreamlineScanX")
    st.write("StreamlineScanX is a powerful document OCR and analysis tool. Follow these steps to make the most out of the app:")

    st.markdown('''
    Refer to get the best out of this app:

    **Upload a document:** \n 
    Click on the "Upload a document" button and select the document you want to process. StreamlineScanX supports both PNG images and PDF files.

    **Image OCR:** \n 
    If you upload a PNG image, StreamlineScanX will automatically perform OCR (Optical Character Recognition) on the image. You will see the uploaded image displayed along with the detected bounding boxes around recognized words. The OCR text will be shown below the image.

    **PDF Processing:** \n 
    For PDF files, you have two options: \n

    a. Complete Text of the PDF: Select this option from the dropdown menu to extract and display the complete text content of the PDF. StreamlineScanX will run OCR on each page of the PDF and provide the text output.

    b. Each Page Text with Image: Select this option to view the OCR results for each page individually. StreamlineScanX will display the page image along with the detected bounding boxes around the recognized words. The OCR text for each page will be shown below the image.

    **Table Detection:** \n 
    StreamlineScanX goes beyond OCR by offering table detection capabilities. When processing documents, it can identify and extract structured information from tables, enabling you to work with tabular data more effectively.

    **Note on OCR accuracy: Keep in mind that OCR accuracy may vary depending on the quality and content of the document. Factors such as document clarity, font style, and formatting can impact the OCR results.**
    
    ''')

    
    

def show_about_streamlineScanX():
    show_about_image_file = 'assets/aboutus.jpg'
    with open(show_about_image_file, "rb") as show_about_image_file:
        encoded_string = base64.b64encode(show_about_image_file.read())
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
            background-size: cover
        }}
        </style>
        """,
        unsafe_allow_html=True
        )
    st.markdown(
        f"""
        <style>
        .stAppViewContainer {{
            background-image: url(data:image/{"png"};base64,{mainpage_encoded_string.decode()});
            background-size: cover
        }}
        </style>
        """,
        unsafe_allow_html=True
        )
    # About PlanSmart section
    st.title('About StreamlineScanX')
    st.markdown('''
    StreamlineScanX is an advanced document OCR and analysis tool designed to streamline your document processing workflow. It leverages the power of Pytesseract, a popular OCR library, to extract text from images and PDFs. With StreamlineScanX, you can easily digitize your documents, extract valuable information, and gain insights from the text data.

    Key features of StreamlineScanX include:

    **Image OCR:** \n 
    Extract text from uploaded PNG images and visualize the bounding boxes of recognized words.

    **PDF Processing:** \n 
    Process multi-page PDF files and obtain text content for each page.

    **Table Detection:** \n 
    Identify tables within documents and extract structured data from tabular information.

    **OCR Visualization:** \n 
    View the original document images alongside the recognized text and bounding boxes.

    **Flexible Output:** \n 
    Choose between obtaining the complete text of the PDF or analyzing each page separately.

    **User-Friendly Interface:** \n 
    StreamlineScanX provides a simple and intuitive interface, making it easy for users to upload documents and view the OCR results.


    StreamlineScanX is a valuable tool for tasks such as digitizing paper documents, extracting information from scanned files, analyzing tabular data, and automating data entry processes. It saves you time and effort by converting document text into editable and searchable format, opening up opportunities for data analysis and further processing.
    ''')


if __name__ == '__main__':
    main()