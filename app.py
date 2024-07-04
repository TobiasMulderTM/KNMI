from flask import Flask, request, jsonify, render_template
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import knmi
import datetime as dt

app = Flask(__name__)

stations = {
    "209": "IJmond",
    "210": "Valkenburg Zh",
    "215": "Voorschoten",
    "225": "IJmuiden",
    "235": "De Kooy",
    "240": "Schiphol",
    "242": "Vlieland",
    "248": "Wijdenes",
    "249": "Berkhout",
    "251": "Hoorn Terschelling",
    "257": "Wijk aan Zee",
    "258": "Houttridijk",
    "260": "De Bilt",
    "265": "Soesterberg",
    "267": "Stavoren",
    "269": "Lelystad",
    "270": "Leeuwarden",
    "273": "Marknesse",
    "275": "Deelen",
    "277": "Lauwersoog",
    "278": "Heino",
    "279": "Hoogeveen",
    "280": "Eelde",
    "283": "Hupsel",
    "285": "Huibertgat",
    "286": "Nieuw Beerta",
    "290": "Twenthe",
    "308": "Cadzand",
    "310": "Vlissingen",
    "311": "Hoofdplaat",
    "312": "Oosterschelde",
    "313": "Vlakke van De Raan",
    "315": "Hansweert",
    "316": "Schaar",
    "319": "Westdorpe",
    "323": "Wilhelminadorp",
    "324": "Stavenisse",
    "330": "Hoek van Holland",
    "331": "Tholen",
    "340": "Woensdrecht",
    "343": "Rotterdam Geulhaven",
    "344": "Rotterdam",
    "348": "Cabauw Mast",
    "350": "Gilze-Rijen",
    "356": "Herwijnen",
    "370": "Eindhoven",
    "375": "Volkel",
    "377": "Ell",
    "380": "Maastricht",
    "391": "Arcen"
}

def fetch_data(station, start_year, end_year):
    start = pd.Timestamp(dt.datetime(int(start_year), 1, 1))
    end = pd.Timestamp(dt.datetime(int(end_year), 12, 31))
    
    fday = knmi.get_day_data_dataframe(stations=[station], start=start, end=end)
    
    # Save the dataframe to a text file
    fday.to_csv(f'weather_data_{station}_{start_year}_{end_year}.txt', sep='\t')
    
    return fday

def generate_plots(df, start_year, end_year, station):
    # Plot temperature
    plt.figure(figsize=(10, 6))
    #df['YYYYMMDD'] = pd.to_datetime(df['YYYYMMDD'], format='%Y%m%d')
    #df.set_index('YYYYMMDD', inplace=True)
    plt.plot(df.index, df['TX']/10, label='Max Temperatuur')
    plt.plot(df.index, df['TN']/10, label='Min Temperatuur')
    plt.title(f'Temperatuur van {start_year} tot {end_year}')
    plt.xlabel('Datum')
    plt.ylabel('Temperatuur (°C)')
    plt.legend()
    temp_img = BytesIO()
    plt.savefig(temp_img, format='png')
    temp_img.seek(0)
    temp_plot_url = base64.b64encode(temp_img.getvalue()).decode()
    plt.close()

    # Plot precipitation
    precipitation_mm = df['RH'] / 10
    plt.figure(figsize=(16, 6))
    plt.plot(precipitation_mm.index, precipitation_mm, lw=0.75, label=f"Gemiddelde dagelijkse neerslag station {stations[str(station)]}")
    plt.xlim(precipitation_mm.index[0], precipitation_mm.index[-1])
    plt.ylim(bottom=precipitation_mm.min())
    plt.ylabel("Dagelijkse neerslag (mm)")
    plt.grid(visible=True)
    plt.legend(loc="best")
    precip_img = BytesIO()
    plt.savefig(precip_img, format='png')
    precip_img.seek(0)
    precip_plot_url = base64.b64encode(precip_img.getvalue()).decode()
    plt.close()
    # Plot groundwater recharge
    evaporation_mm = df['EV24'] / 10  # Assuming 'EV24' is the evaporation column
    gw_recharge = precipitation_mm - evaporation_mm
    gw_rch_180d = gw_recharge.rolling('180D').sum()
    gw_rch_monthly = gw_recharge.rolling("30D").sum()
    
    fig, ax = plt.subplots(figsize=(16, 6))
    ax.plot(gw_rch_monthly.index, gw_rch_monthly, lw=1.0, label="Lopende gemiddelde over 30 dagen station {stations[str(station)]}")
    ax.plot(gw_rch_180d.index, gw_rch_180d, lw=1.0, label="Lopende gemiddelde over 180 dagen station {stations[str(station)]}")
    ax.set_xlim(gw_recharge.index[0], gw_recharge.index[-1])
    ax.set_ylim(bottom=gw_rch_180d.min())
    ax.set_ylabel("Gemiddelde netto neerslag (mm)")
    ax.grid(visible=True)
    ax.legend(loc="best", fontsize=13)
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
                 ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(14)
    recharge_img = BytesIO()
    fig.savefig(recharge_img, format='png')
    recharge_img.seek(0)
    recharge_plot_url = base64.b64encode(recharge_img.getvalue()).decode()
    plt.close()
    
    #Plot Monthly recharge
    gw_rch_monthly = gw_recharge.resample("MS").sum()

    fig, ax = plt.subplots(figsize=(16, 6))
    ax.plot(gw_rch_monthly.index, gw_rch_monthly,marker="o",lw=0.75, label="Gemiddelde maandelijkse grondwateraanvulling station hoekvholland")
    ax.set_xlim(gw_rch_monthly.index[0], gw_rch_monthly.index[-1])
    ax.set_ylim(bottom=gw_rch_monthly.min())
    ax.set_ylabel("Maandelijkse grondwateraanvulling (mm)")
    ax.grid(visible=True)
    ax.legend(loc="best", fontsize=13)
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
                 ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(14)
    recharge_m_img = BytesIO()
    fig.savefig(recharge_m_img, format='png')
    recharge_m_img.seek(0)
    recharge_m_plot_url = base64.b64encode(recharge_m_img.getvalue()).decode()
    plt.close()

    return temp_plot_url, precip_plot_url,recharge_plot_url,recharge_m_plot_url

@app.route('/')
def home():
    return render_template('index.html', stations=stations)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    station = int(data['station'])
    start_year = data['start_year']
    end_year = data['end_year']
    
    df = fetch_data(station, start_year, end_year)
    temp_plot_url, precip_plot_url, recharge_plot_url, recharge_m_plot_url = generate_plots(df, start_year, end_year, station)
    
    return jsonify({'temp_plot_url': temp_plot_url, 'precip_plot_url': precip_plot_url, 'recharge_plot_url': recharge_plot_url, 'recharge_m_plot_url': recharge_m_plot_url})

if __name__ == '__main__':
    app.run(debug=True)
