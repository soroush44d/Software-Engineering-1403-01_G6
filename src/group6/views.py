from django.shortcuts import render, redirect
from django.views import View
from group6.forms import WordForm
from django.contrib import messages
from database.query import create_db_connection, get_user_id_by_username
from database.secret import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
from group6.models import Words, LeitnerBox, Tick8
from datetime import date, timedelta
from django.db.models import Count
from django.db import transaction



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
                for stage in range(1, 9):  # Stage 1 to Stage 8
                    Tick8.objects.create(
                        word=word_instance,
                        user_id=user_id,
                        current_stage=stage
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


class PracticeLeitner(View):
    def get(self, request, box, word_id=None):
        template = 'LeitnerStart.html'
        try:
            db = create_db_connection(DB_HOST, int(DB_PORT), DB_USER, DB_PASSWORD, DB_NAME)
            user_username = request.user.username
            user_id = get_user_id_by_username(db, user_username)
        except Exception as e:
            print(f"Error while connecting to the database: {e}")
            messages.error(request, "Database connection error.")
            return redirect('group6:home')

        if 'red' in request.session:
            print('first red')
            if request.session['red'] == True:
                print('second red')
                action_result = request.GET.get('action')

                processed_word = Words.objects.filter(id=word_id)
                if not processed_word:
                    print("Not here")
                else:
                    processed_word = Words.objects.get(id=word_id)
                    related_leitner = LeitnerBox.objects.get(word__id=word_id)
                    if action_result == 'remember':
                        print(f'res for {processed_word} is remember')
                        related_leitner.move_to_next_box()
                        related_leitner.save()
                    if action_result == 'forgot':
                        print(f'res for {processed_word} is forget')
                        related_leitner.move_to_previous_box()
                        related_leitner.save()
                messages.info(request, "مرور شما به پایان رسید :).")
                del request.session['red']
                if 'word_ids' in request.session:
                    del request.session['word_ids']
                return redirect('group6:home')

        request.session['red'] = False
        # Add ids to user session (store only the ids as a list)
        if 'word_ids' not in request.session:
            word_ids_to_review = list(
                LeitnerBox.objects.filter(user_id=user_id, box_number=box)
                .values_list('word__id', flat=True)
            )
            print(f"creating list for usr {word_ids_to_review}")
            request.session['word_ids'] = word_ids_to_review
            request.session['red']=False
        else:
            print(f'it has this {request.session['word_ids']}')
            words = request.session['word_ids']
            request.session['word_ids'] = words[1:]
            request.session['red'] = False

        # Process words
        if  len(request.session['word_ids'])==1:
            request.session['red'] = True


        if not request.session['word_ids']:
            del request.session['word_ids']
            word_ids_to_review = list(
                LeitnerBox.objects.filter(user_id=user_id, box_number=box)
                .values_list('word__id', flat=True)
            )
            print(f"creating list for usr {word_ids_to_review}")
            request.session['word_ids'] = word_ids_to_review

        try:
            word_id_to_review = request.session['word_ids'][0]
        except (IndexError, KeyError):
            messages.info(request, "هیچ کلمه‌ای برای مرور در این جعبه وجود ندارد.")
            return redirect('group6:home')

        print(word_id_to_review)
        print(box)
        print(user_id)
        if Words.objects.filter(id=word_id_to_review).first():
            word = Words.objects.get(id=word_id_to_review)
        else:
            print('its non')

        # manage result
        action_result = request.GET.get('action')

        processed_word = Words.objects.filter(id=word_id)
        if not processed_word:
            print("Not here")
        else:
            processed_word = Words.objects.get(id=word_id)
            related_leitner = LeitnerBox.objects.get(word__id=word_id)
            if action_result == 'remember':
                print(f'res for {processed_word} is remember')
                related_leitner.move_to_next_box()
                related_leitner.save()
            if action_result == 'forgot':
                print(f'res for {processed_word} is forget')
                related_leitner.move_to_previous_box()
                related_leitner.save()

        #manage redirect
        print(request.session['word_ids'])

        return render(request, template, {'word': word, 'box_number': box})


class Tick8View(View):
    def get(self,request):
        template='tik8.html'
        try:
            db = create_db_connection(DB_HOST, int(DB_PORT), DB_USER, DB_PASSWORD, DB_NAME)
            user_username = request.user.username
            user_id = get_user_id_by_username(db, user_username)
        except Exception as e:
            print(f"Error while connecting to the database: {e}")
            messages.error(request, "Database connection error.")
            return redirect('group6:home')

        tick8_words = Tick8.objects.filter(user_id=user_id)

        stages = {}
        for stage in range(1, 9):  # Stage 1 to Stage 8
            stages[stage] = [
                {
                    "word": tick.word,
                    "remembered": tick.remmembered,
                    "clickable": tick.is_clickable()
                }
                for tick in tick8_words.filter(current_stage=stage)
            ]
        print(stages)
        context = {
            "stages": stages,
            "user_id":user_id
        }
        return render(request, template, context)

class Tick8Practice(View):
    def get(self,request , user_id, stage,word_id=None):
        print(f"user with {user_id} and tage {stage}, word_id {word_id}")
        template = 'TickStart.html'
        if 'red' in request.session:
            print('first red')
            if request.session['red'] == True:
                print('second red')
                action_result = request.GET.get('action')

                processed_word = Words.objects.filter(id=word_id)
                if not processed_word:
                    print("Not here")

                else:
                    processed_word = Words.objects.get(id=word_id)
                    related_tick = Tick8.objects.get(word__id=word_id, current_stage=stage)
                    try:
                        if action_result == 'remember':
                            print('finaly done')
                            related_tick.remmembered = True
                            with transaction.atomic():  # ensure changes are committed
                                related_tick.save()
                            print(f"Updated remembered: {related_tick.remmembered}")
                        elif action_result == 'forgot':
                            print('finaly done')
                            related_tick.remmembered = False
                            with transaction.atomic():  # ensure changes are committed
                                related_tick.save()

                        print(f"Updated remembered: {related_tick.remmembered}")
                    except Exception as e:
                        print(f"Error while saving: {e}")
                messages.info(request, "مرور شما به پایان رسید :).")
                del request.session['red']
                if 'word_ids_t' in request.session:
                    del request.session['word_ids_t']
                return redirect('group6:home')

        request.session['red'] = False
        # Add ids to user session (store only the ids as a list)
        if 'word_ids_t' not in request.session:
            word_ids_to_review = list(
                Tick8.objects.filter(user_id=user_id, current_stage=stage)
                .values_list('word__id', flat=True)
            )
            request.session['word_ids_t'] = word_ids_to_review
            request.session['red'] = False
        else:
            print(f'it has this {request.session['word_ids_t']}')
            words = request.session['word_ids_t']
            request.session['word_ids_t'] = words[1:]
            request.session['red'] = False

        if len(request.session['word_ids_t']) == 1:
            print("len is ==1 red=true")
            request.session['red'] = True

        if not request.session['word_ids_t']:
            del request.session['word_ids_t']
            word_ids_to_review = list(
                Tick8.objects.filter(user_id=user_id, current_stage=stage)
                .values_list('word__id', flat=True)
            )
            print(f"creating list for usr {word_ids_to_review}")
            request.session['word_ids_t'] = word_ids_to_review


        try:
            word_id_to_review = request.session['word_ids_t'][0]
        except (IndexError, KeyError):
            messages.info(request, "هیچ کلمه‌ای برای مرور در این جعبه وجود ندارد.")
            return redirect('group6:home')

        print(word_id_to_review)
        print(stage)
        print(user_id)

        if Words.objects.filter(id=word_id_to_review).exists():
            word = Words.objects.filter(id=word_id_to_review)
        else:
            print('its non')

        # manage result
        action_result = request.GET.get('action')

        processed_word = Words.objects.filter(id=word_id)
        if not processed_word:
            print("Not here")
        else:
            processed_word = Words.objects.get(id=word_id)
            print(f"proces word :{processed_word}")
            related_tick = Tick8.objects.filter(word__id=word_id, current_stage=stage).first()
            print(f"this object :{related_tick}")
            try:
                if action_result == 'remember':
                    print('finaly done')
                    related_tick.remmembered = True
                    with transaction.atomic():  # ensure changes are committed
                        related_tick.save()
                    print(f"Updated remembered: {related_tick.remmembered}")
                elif action_result == 'forgot':
                    print('fss')
                    related_tick.remmembered = False
                    with transaction.atomic():  # ensure changes are committed
                        related_tick.save()
                    print(f"Updated remembered: {related_tick.remmembered}")

                print(f"Updated remembered: {related_tick.remmembered}")

            except Exception as e:
                print(f"Error while saving: {e}")

        print(request.session['word_ids_t'])
        print("sending word:",word)
        return render(request, template, {'word': word, 'stage': stage,'user_id':user_id})


class ShowListView(View):
    def get(self,request):
        template= 'LIst.html'
        try:
            db = create_db_connection(DB_HOST, int(DB_PORT), DB_USER, DB_PASSWORD, DB_NAME)
        except Exception as e:
            print(f"Error while connecting to the database: {e}")
            raise

        user_username = request.user.username
        user_id = get_user_id_by_username(db, user_username)
        if not user_id:
            messages.error(request, "User ID not found.")

        boxes = LeitnerBox.objects.filter(user_id=user_id)
        tick8s = Tick8.objects.filter(user_id=user_id, current_stage=1)

        words = Words.objects.filter(user_id=user_id)



        return render(request, template, {'boxes': boxes, 'ticks':tick8s, 'words':words})





class DeleteWordView(View):

    def get(self, request, word_id):
        db = create_db_connection(DB_HOST, int(DB_PORT), DB_USER, DB_PASSWORD, DB_NAME)
        user_username = request.user.username
        user_id = get_user_id_by_username(db, user_username)

        word = Words.objects.get(id=word_id,user_id=user_id)
        print(word)
        word.delete()
        messages.success(request, "کلمه با موفقیت حذف شد :)")
        return redirect('group6:showlist')

