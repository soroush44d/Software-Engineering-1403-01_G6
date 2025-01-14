from django.shortcuts import render, redirect
from django.views import View
from group6.forms import WordForm
from django.contrib import messages
from database.query import create_db_connection, get_user_id_by_username
from database.secret import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
from group6.models import Words, LeitnerBox, Tick8
from datetime import date, timedelta
from django.db.models import Count



class Home(View):
    form = WordForm

    def get(self, request):
        form = self.form()
        template = 'home.html'
        return render(request, template, {'group_number': '6', 'form': form})

    def post(self, request):
        pass


class AddWords(View):
    form_class = WordForm

    def get(self, request):
        template = 'AddWord.html'
        form = self.form_class
        return render(request, template, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            word = form.cleaned_data['word']
            description = form.cleaned_data['description']
            add_to_leitner = form.cleaned_data['add_to_leitner']
            add_to_tick8 = form.cleaned_data['add_to_tick8']

            try:
                db = create_db_connection(DB_HOST, int(DB_PORT), DB_USER, DB_PASSWORD, DB_NAME)
            except Exception as e:
                print(f"Error while connecting to the database: {e}")  # خطا را چاپ کنید
                raise

            user_username = request.user.username
            user_id = get_user_id_by_username(db, user_username)

            if not user_id:
                print('user not found')
                messages.error(request, "User ID not found.")
                return redirect('group6:home')

            Words.objects.create(
                word=word,
                description=description,
                user_id=user_id,
            )
            word_instance = Words.objects.get(word=word, user_id=user_id)

            if add_to_leitner:
                LeitnerBox.objects.create(
                    word=word_instance,
                    user_id=user_id,
                    box_number=1,
                    next_review_date=date.today() + timedelta(days=1)
                )

            if add_to_tick8:
                Tick8.objects.create(
                    word=word_instance,
                    user_id=user_id,
                )




            messages.success(request, f"Word '{word}' added successfully!")
            return redirect('group6:home')

        messages.error(request, "Invalid form submission.")
        return redirect('group6:home')


class ShowLeitner(View):
    def get(self, request):
        template = 'leitner.html'
        try:
            db = create_db_connection(DB_HOST, int(DB_PORT), DB_USER, DB_PASSWORD, DB_NAME)
        except Exception as e:
            print(f"Error while connecting to the database: {e}")
            raise

        user_username = request.user.username
        user_id = get_user_id_by_username(db, user_username)
        if not user_id:
            messages.error(request, "User ID not found.")

        boxes = LeitnerBox.objects.filter(user_id=user_id).values('box_number').annotate(count=Count('id'))
        box_counts = {box['box_number']: box['count'] for box in boxes}
        print(box_counts)

        all_boxes = {box_number: 0 for box_number in range(1, 6)}
        all_boxes.update(box_counts)
        print(all_boxes)

        return render(request, template, {'leitners': all_boxes})



    def post(self, request):
        pass


class LeitnerReview(View):
    def get(self, request,box):
        template = 'LeitnerStart.html'
        try:
            db = create_db_connection(DB_HOST, int(DB_PORT), DB_USER, DB_PASSWORD, DB_NAME)
        except Exception as e:
            print(f"Error while connecting to the database: {e}")
            raise

        user_username = request.user.username
        user_id = get_user_id_by_username(db, user_username)
        if not user_id:
            messages.error(request, "User ID not found.")
            return redirect('group6:home')
        user_words = LeitnerBox.objects.filter(user_id=user_id, box_number = box)
        return render(request, template, {'words':user_words})

    def post(self, request):
        pass
