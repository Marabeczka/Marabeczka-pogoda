import requests
import pprint
import streamlit as st
import pandas as pd
from streamlit_extras.let_it_rain import rain

WEATHER_CODES = {
        0: "☀️ Czyste niebo",
        1: "🌤️ Głównie bezchmurnie",
        2: "⛅ Częściowe zachmurzenie",
        3: "☁️ Pochmurno",
        45: "🌫️ Mgła",
        48: "🌫️ Mgła osadzająca szadź",
        51: "🌧️ Mżawka: lekka",
        53: "🌧️ Mżawka: umiarkowana",
        55: "🌧️ Mżawka: gęsta",
        56: "❄️💧 Marznąca mżawka: lekka",
        57: "❄️💧 Marznąca mżawka: gęsta",
        61: "☔ Deszcz: słaby",
        63: "☔ Deszcz: umiarkowany",
        65: "☔ Deszcz: ulewny",
        66: "🧊 Marznący deszcz: lekki",
        67: "🧊 Marznący deszcz: mocny",
        71: "❄️ Opady śniegu: słabe",
        73: "❄️ Opady śniegu: umiarkowane",
        75: "❄️ Opady śniegu: intensywne",
        77: "🌨️ Ziarnisty śnieg",
        80: "🌦️ Przelotne opady deszczu: słabe",
        81: "🌦️ Przelotne opady deszczu: umiarkowane",
        82: "🌦️ Przelotne opady deszczu: gwałtowne",
        85: "❄️🌬️ Przelotne opady śniegu: słabe",
        86: "❄️🌬️ Przelotne opady śniegu: mocne",
        95: "⚡ Burza: słaba lub umiarkowana",
        96: "⛈️ Burza z lekkim gradem",
        99: "⛈️ Burza z ciężkim gradem"
    }

def api_miasto(miejsc):
    url_miejsc = "https://nominatim.openstreetmap.org/search"
    parametry_miejsc = {"format": "json", "q": miejsc}
    naglowki = {"User-Agent": "marabeczka"}
    response_miejsc = requests.get(url_miejsc, params = parametry_miejsc, headers = naglowki)
    wynik = response_miejsc.json()
    if response_miejsc.status_code == 200:
        if wynik != []:
            lat = float(wynik[0]["lat"])
            lon = float(wynik[0]["lon"])
            name = wynik[0]["name"]
            return lat, lon, name
        
        return None, None, None
def api_pogoda(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    parametry = {"format": "json", "latitude": lat, "longitude": lon, "current_weather": "true"}
    response = requests.get(url, params = parametry)
    dane = response.json()
    if response.status_code == 200:
        temp = dane['current_weather']['temperature']
        wind = dane['current_weather']['windspeed']
        kod_wmo = dane['current_weather']['weathercode']
        kody = WEATHER_CODES.get(kod_wmo, "Nieznana pogoda")
        mapa_dane = pd.DataFrame({'lat': [lat], 'lon': [lon]})
        
        return temp, wind, kody, mapa_dane
    else:
        return None, None, None, None
def dc_msg(name, kody, temp, wind,):
        if temp < 0:
            color = 15132390
        elif temp <= 10:
            color = 3447003
        elif temp <= 20:
            color = 5763719      
        elif temp <= 30:
            color = 15105570       
        else:
            color = 15548997

        url_dc = st.secrets["DISCORD_WEBHOOK_URL"]
        nowy_post = {
            "embeds": [
                {
                    "title": "Raport Pogodowy",
                    "description": f"W {name},\nCo za oknem: {kody},\nTemperatura: {temp} °C,\nPrędkość wiatru: {wind} km/h, ",
                    "color": color
                }
                ]
        }
        response_discord = requests.post(url_dc, json=nowy_post)
        if response_discord.status_code == 204:
            return True
        else:
            return False



def main():
    st.title("Aplikacja Pogodowa☀️")
    miejsc = st.text_input("Gdzie chcesz sprawdzic pogode? ")
    if miejsc:
        with st.spinner("Pobieram dane."):
            lat, lon, name = api_miasto(miejsc)
            if lat is not None:
                temp, wind, kody, mapa_dane = api_pogoda(lat, lon)
                st.success(f"Znaleziono: {name}")
                st.markdown("---")
                st.header(f"📍{name}")
                st.info(f"### {kody}")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(label = "🌡️ Temperatura", value = f"{temp} °C")
                with col2:
                    st.metric(label = "💨 Predkość Wiatru", value = f"{wind} km/h")
                
                if st.button("Wyslij raport na Discord"):
                    if_true = dc_msg(name, kody, temp, wind,)
                    if if_true:
                        st.success("Wysłano raport!")
                    else:
                        st.error("Coś poszło nie tak z wysyłaniem.")
                    
                with st.expander("🗺️ Zobacz na Mapie"):
                    st.map(mapa_dane)
                with st.expander("Kliknij, aby zobaczyć dokładne współrzędne"):
                    st.write(f"Szerokość geograficzna (Lat): {lat}")
                    st.write(f"Długość geograficzna (Lon): {lon}")
                    st.write("Źródło danych: Open-Meteo")
                if temp < 0:
                    rain(
                        emoji = "🥶",
                        font_size = 54,
                        falling_speed = 3,
                        animation_length = 1
                    )
                elif temp > 25:
                    rain(
                        emoji = "🔥",
                        font_size = 54,
                        falling_speed = 3,
                        animation_length = 1
                    )
            else:
                st.error("Mic nie znalazłem :(")


if __name__ == "__main__":
    main()
