from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def generate_financing_report(financing_data, output_file="financing_report.pdf"):
    """Генерация PDF-отчета о финансировании вузов."""

    # Регистрация шрифта
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'font/DejaVuSans.ttf'))
    c = canvas.Canvas(output_file, pagesize=letter)
    width, height = letter

    c.setFont('DejaVuSans', 12)  # Установка шрифта

    c.drawString(100, height - 50, "Отчет о поквартальном финансировании вузов")
    c.drawString(100, height - 80, "Сокращенное имя | Фактическое финансирование")

    y_position = height - 100
    for data in financing_data:
        c.drawString(100, y_position, f"{data['Сокращенное_имя']} | {data['Фактическое_финансирование']}")
        y_position -= 20  # Переход на следующую строку

    c.save()
    print(f"Отчет сохранен как {output_file}")