from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io


def generate_pdf(user_profile):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)


    c.drawString(100, 750, f"Name: {user_profile.name}")
    c.drawString(100, 730, f"Father's Name: {user_profile.father_name}")
    c.drawString(100, 710, f"Age: {user_profile.age}")
    c.drawString(100, 690, f"Address: {user_profile.address}")



    if user_profile.user_id_proof:
        c.drawString(100, 650, "ID Proof Attached:")
        id_proof_path = user_profile.user_id_proof.path
        c.drawImage(id_proof_path, 100, 550, width=200, height=100)
    else:
        c.drawString(100, 650, "ID Proof: Not provided")


    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
