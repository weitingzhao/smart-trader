import time

import pandas as pd
import ray
from django.shortcuts import render

from cerebro.ray_optimize import RayStrategyOptimize
from cerebro.ray_sample_pi import ProgressActor, sampling_task
from apps.common.models import *
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from bokeh.embed import server_document
from home.forms.strategy_algo_script import StrategyAlgoScriptModelForm
import redis
import json
import threading

def listen_to_redis():
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=1)
    pubsub = redis_client.pubsub()
    pubsub.subscribe("bokeh_plot_channel")

    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
        print("Received message:", message)

def default(request):

    # Start the Redis listener in a separate thread
    listener_thread = threading.Thread(target=listen_to_redis)
    listener_thread.daemon = True
    listener_thread.start()

    # bokeh_script = server_document("http://localhost:5006/my_bokeh_app")

    if request.method == 'POST':
        form = StrategyAlgoScriptModelForm(request.POST)
        if form.is_valid():
            # Process the form data
            print(form.cleaned_data)
            # Get title and text from form.cleaned_data
            title = form.cleaned_data['title']
            text = form.cleaned_data['text']

            # Save to StrategyAlgoScript model
            strategy_algo_script = StrategyAlgoScript(title=title, text=text)
            strategy_algo_script.save()
            # Redirect or show success message
            return render(request,
                          'pages/analytics/market_comparison.html',
                          {'message': 'Form submitted successfully!'})
    algo_script_form = StrategyAlgoScriptModelForm()

    return render(
        request=request,
        template_name='pages/analytics/market_comparison.html',
        context= {
            'parent': 'analytics',
            'segment': 'market_comparison',
            'form': algo_script_form,
            'bokeh_script': 'test'
        })

@csrf_exempt
def save_algo_strategy(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        content = data.get('content', '')
        file_content, created = StrategyAlgoScript.objects.get_or_create(name='default_strategy.py')
        file_content.content = content
        file_content.save()
        return JsonResponse({'success': True})

def load_algo_strategy(request):
    file_content = StrategyAlgoScript.objects.filter(name='default_strategy.py').first()
    content = file_content.content if file_content else ''
    return JsonResponse({'content': content})


def ray_sample_pi():
    # Change this to match your cluster scale.
    NUM_SAMPLING_TASKS = 10
    NUM_SAMPLES_PER_TASK = 10_000_000
    TOTAL_NUM_SAMPLES = NUM_SAMPLING_TASKS * NUM_SAMPLES_PER_TASK

    # Create the progress actor.
    progress_actor = ProgressActor.remote(TOTAL_NUM_SAMPLES)

    # Create and execute all sampling tasks in parallel.
    results = [
        sampling_task.remote(NUM_SAMPLES_PER_TASK, i, progress_actor)
        for i in range(NUM_SAMPLING_TASKS)
    ]

    # Query progress periodically.
    while True:
        progress = ray.get(progress_actor.get_progress.remote())
        print(f"Progress: {int(progress * 100)}%")

        if progress == 1:
            break
        time.sleep(1)

    # Get all the sampling tasks results.
    total_num_inside = sum(ray.get(results))
    pi = (total_num_inside * 4) / TOTAL_NUM_SAMPLES
    print(f"Estimated value of π is: {pi}")

    return pi