"""
Formulaires pour l'application remplacements
"""
from django import forms
from django.contrib.auth import get_user_model
from .models import Absence, Remplacant, Remplacement
from apps.etablissements.models import Matiere, Salle

User = get_user_model()


class AbsenceForm(forms.ModelForm):
    """
    Formulaire pour la création/modification d'une absence
    """
    class Meta:
        model = Absence
        fields = [
            'enseignant', 'type_absence', 'date_debut', 'date_fin',
            'heure_debut', 'heure_fin', 'motif', 'justificatif', 'urgence'
        ]
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'heure_debut': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'heure_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'motif': forms.Textarea(attrs={'rows': 4, 'class': 'form-textarea'}),
            'justificatif': forms.FileInput(attrs={'class': 'form-input'}),
            'urgence': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personnaliser les champs
        self.fields['enseignant'].queryset = User.objects.filter(role='enseignant')
        self.fields['type_absence'].widget.attrs.update({'class': 'form-select'})
        
        # Ajouter les classes CSS pour Tailwind
        for field_name, field in self.fields.items():
            if field_name not in ['urgence', 'justificatif']:
                field.widget.attrs.update({'class': 'form-input'})
    
    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')
        heure_debut = cleaned_data.get('heure_debut')
        heure_fin = cleaned_data.get('heure_fin')
        
        # Vérifier que la date de fin est après la date de début
        if date_debut and date_fin and date_fin < date_debut:
            raise forms.ValidationError("La date de fin doit être postérieure à la date de début.")
        
        # Vérifier que l'heure de fin est après l'heure de début
        if heure_debut and heure_fin and heure_fin <= heure_debut:
            raise forms.ValidationError("L'heure de fin doit être postérieure à l'heure de début.")
        
        return cleaned_data


class RemplacantForm(forms.ModelForm):
    """
    Formulaire pour la création/modification d'un remplaçant
    """
    class Meta:
        model = Remplacant
        fields = [
            'enseignant', 'date_debut_disponibilite', 'date_fin_disponibilite',
            'heures_disponibles', 'matieres_enseignees', 'niveaux_competents',
            'preferences_etablissement', 'tarif_horaire', 'distance_max'
        ]
        widgets = {
            'date_debut_disponibilite': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'date_fin_disponibilite': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'heures_disponibles': forms.Textarea(attrs={'rows': 3, 'class': 'form-textarea'}),
            'niveaux_competents': forms.CheckboxSelectMultiple(),
            'preferences_etablissement': forms.Textarea(attrs={'rows': 3, 'class': 'form-textarea'}),
            'tarif_horaire': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-input'}),
            'distance_max': forms.NumberInput(attrs={'class': 'form-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personnaliser les champs
        self.fields['enseignant'].queryset = User.objects.filter(role='enseignant')
        self.fields['matieres_enseignees'].queryset = Matiere.objects.filter(actif=True)
        self.fields['matieres_enseignees'].widget.attrs.update({'class': 'form-select'})
        
        # Ajouter les classes CSS pour Tailwind
        for field_name, field in self.fields.items():
            if field_name not in ['niveaux_competents', 'matieres_enseignees']:
                field.widget.attrs.update({'class': 'form-input'})
    
    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut_disponibilite')
        date_fin = cleaned_data.get('date_fin_disponibilite')
        
        # Vérifier que la date de fin est après la date de début
        if date_debut and date_fin and date_fin < date_debut:
            raise forms.ValidationError("La date de fin doit être postérieure à la date de début.")
        
        return cleaned_data


class RemplacementForm(forms.ModelForm):
    """
    Formulaire pour la création/modification d'un remplacement
    """
    class Meta:
        model = Remplacement
        fields = [
            'absence', 'remplacant', 'date_remplacement', 'heure_debut',
            'heure_fin', 'salle', 'commentaires', 'tarif_applique', 'heures_remunerees'
        ]
        widgets = {
            'date_remplacement': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'heure_debut': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'heure_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'commentaires': forms.Textarea(attrs={'rows': 4, 'class': 'form-textarea'}),
            'tarif_applique': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-input'}),
            'heures_remunerees': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personnaliser les champs
        self.fields['absence'].queryset = Absence.objects.filter(statut='declaree')
        self.fields['remplacant'].queryset = Remplacant.objects.filter(statut='disponible')
        self.fields['salle'].queryset = Salle.objects.filter(actif=True)
        
        # Ajouter les classes CSS pour Tailwind
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-input'})
    
    def clean(self):
        cleaned_data = super().clean()
        heure_debut = cleaned_data.get('heure_debut')
        heure_fin = cleaned_data.get('heure_fin')
        
        # Vérifier que l'heure de fin est après l'heure de début
        if heure_debut and heure_fin and heure_fin <= heure_debut:
            raise forms.ValidationError("L'heure de fin doit être postérieure à l'heure de début.")
        
        return cleaned_data


class FiltreAbsencesForm(forms.Form):
    """
    Formulaire de filtrage des absences
    """
    statut = forms.ChoiceField(
        choices=[('', 'Tous les statuts')] + list(Absence.STATUT_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    type_absence = forms.ChoiceField(
        choices=[('', 'Tous les types')] + list(Absence.TYPE_ABSENCE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
    )
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
    )


class FiltreRemplacantsForm(forms.Form):
    """
    Formulaire de filtrage des remplaçants
    """
    statut = forms.ChoiceField(
        choices=[('', 'Tous les statuts')] + list(Remplacant.STATUT_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    matiere = forms.ModelChoiceField(
        queryset=Matiere.objects.filter(actif=True),
        required=False,
        empty_label="Toutes les matières",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    note_min = forms.FloatField(
        required=False,
        min_value=0,
        max_value=5,
        widget=forms.NumberInput(attrs={'step': '0.1', 'class': 'form-input'})
    )

