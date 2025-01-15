if request.session.get('red', False):
    print('im here')
    try:
        db = create_db_connection(DB_HOST, int(DB_PORT), DB_USER, DB_PASSWORD, DB_NAME)
    except Exception as e:
        print(f"Error while connecting to the database: {e}")
        messages.error(request, "Database connection error.")
        return redirect('group6:home')

    user_username = request.user.username
    user_id = get_user_id_by_username(db, user_username)
    action_result = request.GET.get('action')
    word = LeitnerBox.objects.filter(user_id=user_id, box_number=box, word__id=word_id).first()

    # اعمال تغییرات در وضعیت کلمه
    if action_result == 'remember':
        word.move_to_next_box()
        word.save()
    if action_result == 'forgot':
        word.move_to_previous_box()
        word.save()

    messages.info(request, "دوره این جعبه ی شما به پایان رسید :) ")
    del request.session['red']
    del request.session['word_count']
    del request.session['user_review_count']
    return redirect("group6:home")

template = 'LeitnerStart.html'
try:
    db = create_db_connection(DB_HOST, int(DB_PORT), DB_USER, DB_PASSWORD, DB_NAME)
except Exception as e:
    print(f"Error while connecting to the database: {e}")
    messages.error(request, "Database connection error.")
    request.session['red'] = False
    del request.session['word_count']
    del request.session['user_review_count']
    return redirect('group6:home')

user_username = request.user.username
user_id = get_user_id_by_username(db, user_username)
word_count = LeitnerBox.objects.filter(user_id=user_id, box_number=box).count()
print(f"word count = {word_count}")

# اگر مقدار word_count قبلاً در سشن ذخیره شده باشد، آن را نادیده می‌گیریم
if 'word_count' not in request.session:
    request.session['word_count'] = word_count
if 'user_review_count' not in request.session:
    request.session['user_review_count'] = 0

# مقداردهی برای user_review_count

user_review_count = request.session['user_review_count']
user_review_count += 1
request.session['user_review_count'] = user_review_count

if not user_id:
    messages.error(request, "User ID not found.")
    del request.session['red']
    del request.session['word_count']
    del request.session['user_review_count']
    return redirect('group6:home')

if word_id is None:
    word = LeitnerBox.objects.filter(user_id=user_id, box_number=box).first()
else:
    word = LeitnerBox.objects.filter(user_id=user_id, box_number=box, word__id=word_id).first()

if not word:
    print("im in not word")
    messages.info(request, "این جعبه خالیه و کلمه ای واسه مرور نیست :)")
    if request.session['red']:
        del request.session['red']
    del request.session['word_count']
    del request.session['user_review_count']
    return redirect('group6:home')

# گرفتن همه کلمات موجود در جعبه
all_words = LeitnerBox.objects.filter(user_id=user_id, box_number=box).order_by('id')
word_ids = list(all_words.values_list('id', flat=True))

# پیدا کردن ایندکس کلمه فعلی و انتخاب کلمه بعدی
current_index = word_ids.index(word.id)
next_index = (current_index + 1) % len(word_ids)
next_word = all_words[next_index]

print(f"{request.session['user_review_count']} > {request.session['word_count']}")
if request.session['user_review_count'] >= request.session['word_count']:
    request.session['red'] = True

# handle next state of leitner
action_result = request.GET.get('action')
print(action_result)
if action_result == 'remember':
    print(f'res for {word} is remember')
    word.move_to_next_box()
    word.save()
if action_result == 'forgot':
    print(f'res for {word} is forget')
    word.move_to_previous_box()
    word.save()

# آماده‌سازی context برای نمایش
context = {
    'word': word,
    'next_word_id': next_word.word.id,
}

return render(request, template, context)