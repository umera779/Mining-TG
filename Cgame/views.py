from django.shortcuts import render, redirect
from .models import Counter, TaskList, Boost, Mining, Level, CustomUser, ButtonState
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.auth import login, get_backends
from django.utils.timezone import now
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sessions.models import Session
from .forms import CustomUserCreationForm


@login_required
def home(request):
    mining_speed = request.user.mining.speed
    # Get the counter object associated with the current user

    counter = request.user.counter
    user_balance = request.user.counter.value
    level = "Learner"
    if user_balance > 15000000:
        level = "newbie"
    if user_balance >= 24000000 :
        level = "Amature"
    if user_balance >= 100000000:
        level = "Pro"
    if user_balance >= 500000000:
        level = "Elite"

    players = Counter.objects.all().order_by('-value')[:3]  # Get top 10
    
    leaderboard = []
    
    if len(players) > 0:
        leaderboard.append({
            'rank': 1,
            'username': players[0].user.username,
            'balance': players[0].value
        })
    if len(players) > 1:
        leaderboard.append({
            'rank': 2,
            'username': players[1].user.username,
            'balance': players[1].value
        })
    if len(players) > 2:
        leaderboard.append({
            'rank': 3,
            'username': players[2].user.username,
            'balance': players[2].value
        })

    return render(request, 'pain.html', {'counter': counter,'mining_speed': mining_speed, 'level':level, 'leaderboard': leaderboard})


@login_required
def get_button_state(request):
    if request.user.is_authenticated:
        button_state, created = ButtonState.objects.get_or_create(user=request.user)
        remaining_time = button_state.get_remaining_time()
        return JsonResponse({
            'state': button_state.state,
            'remaining_time': remaining_time
        })
    return JsonResponse({'state': 'unclicked', 'remaining_time': 0})

@login_required
def update_button_state(request):
    if request.method == 'POST' and request.user.is_authenticated:
        button_state, created = ButtonState.objects.get_or_create(user=request.user)
        button_state.state = 'clicked'
        button_state.last_clicked = now()
        button_state.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def increment_counter(request):
    if request.method == 'POST' and request.user.is_authenticated:
        # Increment the counter
        mining_speed = request.user.mining  
        mining_goat = mining_speed.speed
        counter = request.user.counter
        counter.value += int(mining_goat)
        counter.save()

        # Update the button state
        button_state, _ = ButtonState.objects.get_or_create(user=request.user)
        button_state.state = "clicked"
        button_state.last_clicked = now()
        button_state.save()

        formatted_counter_value = f"{counter.value:,}"
        return JsonResponse({'counter_value': formatted_counter_value, 'button_state': button_state.state})

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def boost(request):
    boosting_rate = Boost.objects.filter(assigned_users=request.user)
    # Get the boosts available to the current user
    # boosting_rate = request.user.boost
    mining_speed = request.user.mining
    counter = request.user.counter

    if request.method == "POST":
        boost_rate = request.POST.get('booster_value')
        needed = request.POST.get('needed_value')
        boost_id = request.POST.get('boost_id')
        if boost_rate and boost_id:
            if counter.value <= int(needed):
                response_message = "Insufficient Balance"
                messages.info(request, response_message)
                return redirect('/boost')
            else:
                counter.value -= int(needed)
                counter.save()
                mining_speed.speed += int(boost_rate)
                mining_speed.save()
                boost_delete = Boost.objects.get(id=boost_id)
                boost_delete.assigned_users.remove(request.user)
                response_message = "Successfully Boosted"
                messages.success(request, response_message)
        
                return redirect('/boost')
    context = {
        'boosting_rate': boosting_rate,
    }
    return render(request, 'boost.html', context)


@login_required
def taskList(request):
    counter = request.user.counter
    user_tasks = TaskList.objects.filter(assigned_users=request.user)

    if request.method == "POST":
        task_value = request.POST.get('taskvalue')
        task_id = request.POST.get('task_id')
        print(task_id)
        redirect_url = request.POST.get('redirect_url')

        if task_value and task_id:
            counter.value += int(task_value)
            counter.save()

            task = TaskList.objects.get(id=task_id)
            task.assigned_users.remove(request.user)
            return redirect(redirect_url, permanent=True)
            messages.success(request, f"Task '{task.Taskname}' completed successfully!")
        return redirect('/task')

    context = {"tasklist": user_tasks}
    return render(request, 'task.html', context)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()            
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

@login_required
def wallet(request):
    return render(request, 'wallet.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            Counter.objects.create(user=user, value=2000)
            Mining.objects.create(user=user, speed=3000)

            boost = Boost.objects.create(
                boost_name='One time boost',
                boost_value=1000,
                needed_coin=20,
                level='Initial')
            boost.assigned_users.add(user)

            Level.objects.create(user=user, level=1)
            backend = get_backends()[0]  # Select the first backend (modify if needed)
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"

            login(request, user)
            return redirect('home')

    else:
        form = CustomUserCreationForm()

    return render(request, 'signup.html', {'form': form})
