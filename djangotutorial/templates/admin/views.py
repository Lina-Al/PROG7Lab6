from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from polls.models import Question
from .serializers import QuestionStatsSerializer
from django.db.models import Count

class PollStatsView(APIView):
    def get(self, request, pk):
        """
        Получить статистику для конкретного голосования.
        """
        question = Question.objects.prefetch_related('choice_set').get(pk=pk)
        serializer = QuestionStatsSerializer(question)
        return Response(serializer.data)


class PollListView(ListAPIView):
    """
    Список голосований с фильтрацией и сортировкой.
    """
    serializer_class = QuestionStatsSerializer

    def get_queryset(self):
        queryset = Question.objects.all()

        # Фильтрация по дате
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(pub_date__range=[start_date, end_date])

        # Сортировка по популярности
        sort_by_popularity = self.request.query_params.get('sort_by_popularity')
        if sort_by_popularity:
            queryset = queryset.annotate(total_votes=Count('choice__votes')).order_by('-total_votes')

        return queryset
    
import matplotlib.pyplot as plt
from io import BytesIO
import base64

class PollChartView(APIView):
    def get(self, request, pk):
        """
        Генерация диаграммы для голосования.
        """
        question = Question.objects.prefetch_related('choice_set').get(pk=pk)
        labels = [choice.choice_text for choice in question.choice_set.all()]
        votes = [choice.votes for choice in question.choice_set.all()]

        plt.figure(figsize=(10, 6))
        plt.bar(labels, votes, color='skyblue')
        plt.title(question.question_text)
        plt.ylabel('Голоса')
        plt.xlabel('Варианты')
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()

        graphic = base64.b64encode(image_png).decode('utf-8')
        return Response({'chart': graphic})


import csv
from django.http import HttpResponse

class PollExportCSVView(APIView):
    def get(self, request, pk):
        question = Question.objects.prefetch_related('choice_set').get(pk=pk)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{question.question_text}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Вариант', 'Голоса'])
        for choice in question.choice_set.all():
            writer.writerow([choice.choice_text, choice.votes])

        return response
def search_polls(request):
    return render(request, 'polls/search.html')
