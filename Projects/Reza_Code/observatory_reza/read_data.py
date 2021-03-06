# We need to import these modules to get started
drive_path = 'e:/'
import numpy as np
import pandas as pd
import os
import sys
from decoder import *
from allensdk.core.brain_observatory_cache import BrainObservatoryCache
from allensdk.brain_observatory.static_gratings import StaticGratings
manifest_path = os.path.join(drive_path,'BrainObservatory/manifest.json')

boc = BrainObservatoryCache(manifest_file=manifest_path)

#label extractor
def labeled_data_extractor(stim_info, type_of_labels):
    '''Assignes lables for eah stimuli, Type_of_lable can be ['orientation'] or ['temporal_frequency'] or both. stim_info is a panda data_frame produces by BrainObservatoryCashe '''
    si = stim_info.copy();
    if len(type_of_labels) == 1:
        temp_si = si[type_of_labels[0]].replace(si[type_of_labels[0]].unique(), range(len(si[type_of_labels[0]].unique())));
        return(temp_si.values.astype(int))
    elif ['temporal_frequency', 'orientation'] in type_of_labels:
        0;
# Pick an experiment container (:)--
experiment_container_v1_cux2 = boc.get_experiment_containers(targeted_structures=['VISp'],cre_lines=['Cux2-CreERT2'],imaging_depths=[275]);
#experiment_container_v1_cux2 = boc.get_experiment_containers(targeted_structures=['VISp'],cre_lines=['Cux2-CreERT2']);

# choose an animal
animal_number=0;
experiment_container_id = experiment_container_v1_cux2[animal_number]['id'];
experiment_information = boc.get_ophys_experiments(experiment_container_ids=[experiment_container_id]);
cell_specimen = boc.get_cell_specimens(experiment_container_ids=[experiment_container_id]);

#choose session ession B
session_id = experiment_information[1]['id']
data_set = boc.get_ophys_experiment_data(ophys_experiment_id= session_id)

# Get DG
from allensdk.brain_observatory.drifting_gratings import DriftingGratings
dg = DriftingGratings(data_set=data_set)

# Get X and Y  (data and label)
Y_original = labeled_data_extractor(dg.stim_table,['orientation']);
X_original = dg.mean_sweep_response.values;

print('Done with loading stuff')

# load firing rates, read dsi
fr = np.load('fr.npy')
dsi = np.load('All_DSI_rate.npy')
X_reduced_original = X_original[:,:-2]

# Run SVM compaere sim vs. shuffle
#svm_decoder(X_reduced_original,Y_original,fr,dg)
svm_decoder_dsi(X_reduced_original,Y_original,fr,dg,dsi)
#

#svm_decoder(fr,Y_original,dg)

#fisher

tr = np.arange(9)+2

of_vec = []
sf_vec = []
fr_of_vec = []
fr_sf_vec = []
num_repeat = 50;
for j in tr:
    sf_sum = 0
    of_sum = 0
    for r in range(num_repeat):
        of,sf = fisher_analysis(X_reduced_original[:,(np.argsort(dsi.flatten()))[-j - 1:-1]],dg)
        of_sum += of/num_repeat
        sf_sum += sf/num_repeat
    of_vec = of_vec + [of_sum]
    sf_vec = sf_vec + [sf_sum]
for j in tr:
    fr_sf_sum = 0
    fr_of_sum = 0
    for r in range(20):
        of,sf = fisher_analysis(fr[:,(np.argsort(dsi.flatten()))[-j - 1:-1]],dg)
        fr_of_sum += of/20.
        fr_sf_sum += sf/20.
    fr_of_vec = fr_of_vec + [fr_of_sum]
    fr_sf_vec = fr_sf_vec + [fr_sf_sum]
plt.figure()
#plt.plot(tr, of_vec, tr, sf_vec, 'r--', tr, fr_of_vec, 'k', tr, fr_sf_vec)
plt.plot(tr, fr_of_vec, 'k', tr, fr_sf_vec)
#plt.legend(['Sim (Ca)', 'Shuf (Ca)', 'Sim (FR)', 'Shuf (FR)'])

plt.legend(['Sim (FR)', 'Shuf (FR)'])
plt.ylabel('Linear Fisher Information')
plt.xlabel('Number of cells with the largest DSI')
plt.show()





