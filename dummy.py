import qweb

if __name__ == "__main__":

    qweb.sendRequest('https://localhost:8080/webService/logger.php?action=setCurrentState&loggable_category_id=2&state=ighn_temp_1k=4.054;ighn_temp_sorb=5.1;ighn_temp_mix=4609.0;ighn_power_mix=0.0;ighn_power_still=0.0;ighn_power_sorb=0.0;ighn_pres_g1=0.0;ighn_pres_g2=584.4;ighn_pres_g3=991.7;ighn_pres_p1=0.02;ighn_pres_p2=0.011;ighn_nv=0.0;;ighn_power_mix_range=50.0;ighn_valves=X0A0C2PA0A00781S0O0E5')

