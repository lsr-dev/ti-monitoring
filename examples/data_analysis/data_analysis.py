from mylibrary import *
from myconfig import *

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

def comma_format(x, pos):
    return str(x).replace('.', ',')

# specify the file directory and name if it differs from the name in the config file
file_dir = '/home/ubuntu/'
file_name = 'data_2026_2.hdf5'
file_path = file_dir + file_name

#specify export path
export_dir = '/home/ubuntu/export/'

# get basic data and availability data for all cis
all_data = []
all_availability_data = {}
print("getting data")
for index, ci in get_data_of_all_cis(file_path).iterrows():
    print("getting data for " + ci['ci'])
    availability_data = get_availability_data_of_ci(file_path, ci['ci'])
    # selection of time window
    availability_data = availability_data[availability_data['times']>pd.Timestamp('2026-02-01T00:00:0.0').tz_localize('Europe/Berlin')]
    availability_data = availability_data[availability_data['times']<pd.Timestamp('2026-03-01T00:00:0.0').tz_localize('Europe/Berlin')]
    all_availability_data[f"{ci['ci']}"] = availability_data
    # get first and last timestamp of window
    first_timestamp = availability_data['times'].iloc[0]
    last_timestamp = availability_data['times'].iloc[-1]
    expected_number_of_data_points = int(round(pd.Timedelta(last_timestamp.replace(second=0, microsecond=0)
- first_timestamp.replace(second=0, microsecond=0)).total_seconds())/300) + 1
    number_of_dropped_data_points = expected_number_of_data_points - len(availability_data['values'])
    entry = {
        "ci_name" : ci['ci'] + ', ' + ci['product'] + ', ' + ci['name'] + '\n' + ci['organization'],
        "available" : len(availability_data[availability_data['values']==1]),
        "unavailable" : len(availability_data[availability_data['values']==0]),
        "unknown" : number_of_dropped_data_points,
        "first_timestamp" : first_timestamp,
        "last_timestamp" : last_timestamp,
        "expected_number_of_data_points" : expected_number_of_data_points
    }
    all_data.append(entry)
all_data = pd.DataFrame(all_data)
print(all_data)

combined_availability_data = pd.concat(
    [df.set_index("times").rename(columns={"values": name})
     for name, df in all_availability_data.items()],
    axis=1,
    join="outer"
)
combined_availability_data = combined_availability_data.astype("Int64")
# export combined availability data to csv file
export_file_path = export_dir + file_name.replace('.hdf5', '_availability_data.csv')
combined_availability_data.to_csv(export_file_path)

# plot cis that were unavailable
plot_data = all_data[all_data['unavailable']>0].sort_values(by = 'unavailable')
print(plot_data)

data_start = plot_data['first_timestamp'].min().strftime('%d.%m.%Y %H:%M:%S Uhr')
data_end = plot_data['last_timestamp'].max().strftime('%d.%m.%Y %H:%M:%S Uhr')
names = plot_data['ci_name']
data = plot_data['unavailable'].values*5/60
fig, ax = plt.subplots(figsize=(21.0,29.7))
barh = ax.barh(names, data)
ax.bar_label(barh, labels=[f"{value:,.2f}".replace('.', ',') for value in data], fontsize=14)
ax.text(
    data.max()/4,
    len(data)/6,
    """Die Berechung der Ausfallzeiten erfolgte durch Multiplikation
der Anzahl der Datenpunkte 'nicht verfügbar' mit 5 Minuten,
der Dauer eines Abfrageintervalls. Die Daten wurden von der
öffentlichen TI-Lage-Schnittstelle der gematik GmbH abgerufen.
Bei der Interpretation sind demensprechend die Hinweise in der
Dokumentation der Schnittstelle zu berücksichtigen. Weitere
Informationen unter https://github.com/gematik/api-tilage.
Alle Angaben ohne Gewähr.""",
    fontsize=14
)
fig.suptitle("Störungen zentraler TI-Komponenten in Stunden\nim Zeitraum " + data_start + ' bis ' + data_end, fontsize=32)
ax.set_frame_on(False)
ax.get_xaxis().set_visible(False)
plt.yticks(fontsize=12)
plt.tight_layout(rect=[0, 0, 1.0, 0.98])
plt.autoscale(enable=True, axis='y', tight=True)
#plt.show()
export_file_path = export_dir + file_name.replace('.hdf5', '_plot.pdf')
plt.savefig(export_file_path)

# export plot data to csv file
export_file_path = export_dir + file_name.replace('.hdf5', '_plot_data.csv')
plot_data.to_csv(export_file_path, index = False)
