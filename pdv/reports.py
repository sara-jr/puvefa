from .models import Article, ArticleSaleReport, Sale, SingleSale, SaleReport,\
    MedicalConsultation, MedicalConsultationReport


def generate_reports(date):
    '''
        Genera los reportes de ventas para cada articulo y generales
    '''
    article_reports: dict[int, ArticleSaleReport] = {}
    sales = Sale.objects.filter(date__date=date)
    single_sales = SingleSale.objects.filter(sale__in=sales)
    sale_report = SaleReport(date=date, sale_count=single_sales.count(), total_cost=0, total_sold=0)

    # Generar los reportes de ventas de articulos
    for single_sale in single_sales:
        article_id = single_sale.article.id
        quantity = single_sale.quantity
        price = single_sale.article.price
        cost = single_sale.article.purchase_price

        # Si no existe ya un reporte para el articulo en el dia indicado, crearlo
        if article_id not in article_reports:
            article_reports[article_id] = ArticleSaleReport(article=single_sale.article,
                date=date, quantity=quantity, total_cost=cost*quantity, total_sold=price*quantity)
        else:
            article_reports[article_id].quantity += quantity
            article_reports[article_id].total_cost += quantity*cost
            article_reports[article_id].total_sold += quantity*price

    # Guardar los reporte de ventas de articulos en la base de datos
    for article_report in article_reports.values():
        article_report.save()
        # Accumular los costos y ventas totales para el reporte del dia
        sale_report.total_cost += article_report.total_cost
        sale_report.total_sold += article_report.total_sold
    sale_report.save()


def generate_consultation_report(date):
    report = MedicalConsultationReport(date=date)
    for consultation in MedicalConsultation.objects.filter(date=date):
        report.total += consultation.price
    report.save()
        
