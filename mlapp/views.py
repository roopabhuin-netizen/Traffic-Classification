import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.shortcuts import render, redirect
from django.conf import settings
import joblib
import numpy as np

# Load the trained model
model_path = os.path.join(settings.BASE_DIR, 'mlapp', 'rf_full_pipeline.joblib')
model = joblib.load(model_path)


def upload_page(request):
    """Render the upload page"""
    return render(request, 'mlapp/upload.html')


def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        csv_file = request.FILES['file']

        # Read CSV
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            return render(request, 'mlapp/upload.html', {
                'error': f"Failed to read CSV: {e}"
            })

        # Predict (MODEL RETURNS STRING LABELS)
        try:
            preds = model.predict(df)
            df['prediction'] = pd.Series(preds).astype(str).str.lower()
        except Exception as e:
            return render(request, 'mlapp/upload.html', {
                'error': f"Prediction error: {e}"
            })

        # -------------------------------
        # MULTI-CLASS COUNTS
        # -------------------------------
        class_counts = df['prediction'].value_counts().to_dict()

        # Define attack classes
        attack_classes = ['bandwidth', 'controller', 'flowtable']

        # Total attack count (all attack types)
        attack_count = sum(class_counts.get(cls, 0) for cls in attack_classes)
        normal_count = class_counts.get('normal', 0)

        # -------------------------------
        # SAVE CSV IF ATTACK EXISTS
        # -------------------------------
        csv_file_url = None
        if attack_count > 0:
            attack_df = df[df['prediction'].isin(attack_classes)]
            csv_path = os.path.join(settings.MEDIA_ROOT, 'predictions.csv')
            attack_df.to_csv(csv_path, index=False)
            csv_file_url = settings.MEDIA_URL + 'predictions.csv'

        # -------------------------------
        # PIE CHART (MULTI-CLASS)
        # -------------------------------
        color_map = {
            'normal': "#2BDB21",
            'bandwidth': "#CBAE0B",
            'controller': "#E83698",
            'flowtable': "#1B44D6"
        }

        labels = list(class_counts.keys())
        sizes = list(class_counts.values())
        colors = [color_map[label] for label in labels]

        plt.figure(figsize=(6, 6), facecolor='white')
        plt.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            wedgeprops={'edgecolor': 'black', 'linewidth': 1}
        )
        plt.title('Traffic Classification Distribution', color='black')

        pie_chart_path = os.path.join(settings.MEDIA_ROOT, 'pie_chart.png')
        plt.savefig(pie_chart_path, bbox_inches='tight')
        plt.close()

        # -------------------------------
        # CONTEXT TO RESULT PAGE
        # -------------------------------
        context = {
            'pie_chart': settings.MEDIA_URL + 'pie_chart.png',
            'class_counts': class_counts,
            'attack_count': attack_count,
            'normal_count': normal_count,
            'total': len(df)
        }

        if csv_file_url:
            context['csv_file'] = csv_file_url

        return render(request, 'mlapp/result.html', context)

    return redirect('upload_page')



from django.shortcuts import render

def home(request):
    return render(request, 'mlapp/home.html')

from django.shortcuts import render

def contact(request):
    return render(request, 'mlapp/contact.html')





from django.shortcuts import render
from .forms import ContactForm

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()   # Save to DB
            return render(request, "mlapp/contact_success.html")
    else:
        form = ContactForm()

    return render(request, "mlapp/contact.html", {"form": form})









