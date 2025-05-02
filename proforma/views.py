from django.shortcuts import render,redirect
from django.conf import settings
from .forms import VisitForm, CostoPredictionForm
from .utils.load_model import load_model
import numpy as np

# Create your views here.
def schedule_visit(request):
    if request.method == 'POST':
        form = VisitForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = VisitForm()
    return render(request, 'proforma/schedule_visit.html', {'form': form})

#modelo para prediccion del costo con el modelo de regresion lineal

# Inicializa tu modelo con los pesos y el sesgo entrenados (ejemplo)
#path/to/linear_regression_model.pkl
model = load_model('proforma/utils/linear_regression_modelC.pkl')

def predict_product_cost(request):
    if request.method == 'POST':
        form = CostoPredictionForm(request.POST)
        if form.is_valid():
            categoria = form.cleaned_data['categoria']
            modelo = form.cleaned_data['modelo']
            acabado = form.cleaned_data['acabado']
            seguridad = form.cleaned_data['seguridad']
            alto = form.cleaned_data['alto']
            ancho = form.cleaned_data['ancho']
            
            features = np.array([categoria, modelo, acabado, seguridad, alto, ancho])
            predicted_cost = model.predict(features)
            return render(request, 'proforma/prediction_result.html', {'predicted_cost': predicted_cost})
    else:
        form = CostoPredictionForm()
    return render(request, 'proforma/predict_product_cost.html', {'form': form})