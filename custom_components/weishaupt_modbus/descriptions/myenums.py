"""Enums."""

from enum import IntEnum


class SystemOperationMode(IntEnum):
    """Enum."""

    system_operating_mode_automatic = 0
    system_operating_mode_heating = 1
    system_operating_mode_cooling = 2
    system_operating_mode_summer = 3
    system_operating_mode_standby = 4
    system_operating_mode_second_heat_source = 5


class DomesticHotWaterConfiguration(IntEnum):
    """Domestic hot water configuration."""

    domestic_hot_water_configuration_off = 0
    domestic_hot_water_configuration_diverter_valve = 1
    domestic_hot_water_configuration_pump = 2


class HeatingCircuitWaterConfiguration(IntEnum):
    """Heating circuit water configuration."""

    heating_circuit_water_configuration_off = 0
    heating_circuit_water_configuration_diverter_valve = 1
    heating_circuit_water_configuration_pump = 2
    heating_circuit_water_configuration_setpoint_pump_m1 = 3


class HeatPumpConfiguration(IntEnum):
    """Heat pump configuration."""

    heat_pump_configuration_not_configured = 0
    heat_pump_configuration_heating = 1
    heat_pump_configuration_heating_cooling_2 = 2
    heat_pump_configuration_heating_cooling_3 = 3
    heat_pump_configuration_heating_hot_water = 4


class HeatPumpRestMode(IntEnum):
    """Heat pump rest mode."""

    heat_pump_rest_mode_off = 0
    heat_pump_rest_mode_80_percent = 1
    heat_pump_rest_mode_60_percent = 2
    heat_pump_rest_mode_40_percent = 3


class HeatingCircuitDemand(IntEnum):
    """Heating circuit demand."""

    heating_circuit_demand_off = 0
    heating_circuit_demand_weather_compensated = 1
    heating_circuit_demand_room_control = 2
    heating_circuit_demand_constant = 3


class HeatingCircuitOperation(IntEnum):
    """Heating circuit operation mode."""

    heating_circuit_operation_mode_automatic = 0
    heating_circuit_operation_mode_comfort = 1
    heating_circuit_operation_mode_normal = 2
    heating_circuit_operation_mode_lowering = 3
    heating_circuit_operation_mode_standby = 4


class SecondHeatSourceStatus(IntEnum):
    """Second heat source status."""

    second_heat_source_status_off = 0
    second_heat_source_status_on = 1


class SecondHeatSourceConfiguration(IntEnum):
    """Second heat source configuration."""

    second_heat_source_configuration_0 = 0
    second_heat_source_configuration_1 = 1
    second_heat_source_configuration_255 = 255


class ElectricHeater1Configuration(IntEnum):
    """Electric heater 1 configuration."""

    second_heat_source_electric_heater_1_configuration_enabled = 5
    second_heat_source_electric_heater_1_configuration_disabled = 225


class ElectricHeater2Configuration(IntEnum):
    """Electric heater 2 configuration."""

    second_heat_source_electric_heater_2_configuration_enabled = 6
    second_heat_source_electric_heater_2_configuration_disabled = 225


class HeatingCircuitPartyPause(IntEnum):
    """Heating circuit party and pause mode."""

    heating_circuit_pause_12 = 1
    heating_circuit_pause_11_5 = 2
    heating_circuit_pause_11 = 3
    heating_circuit_pause_10_5 = 4
    heating_circuit_pause_10 = 5
    heating_circuit_pause_9_5 = 6
    heating_circuit_pause_9 = 7
    heating_circuit_pause_8_5 = 8
    heating_circuit_pause_8 = 9
    heating_circuit_pause_7_5 = 10
    heating_circuit_pause_7 = 11
    heating_circuit_pause_6_5 = 12
    heating_circuit_pause_6 = 13
    heating_circuit_pause_5_5 = 14
    heating_circuit_pause_5 = 15
    heating_circuit_pause_4_5 = 16
    heating_circuit_pause_4 = 17
    heating_circuit_pause_3_5 = 18
    heating_circuit_pause_3 = 19
    heating_circuit_pause_2_5 = 20
    heating_circuit_pause_2 = 21
    heating_circuit_pause_1_5 = 22
    heating_circuit_pause_1 = 23
    heating_circuit_pause_0_5 = 24
    heating_circuit_party_pause_automatic = 25
    heating_circuit_party_0_5 = 26
    heating_circuit_party_1 = 27
    heating_circuit_party_1_5 = 28
    heating_circuit_party_2 = 29
    heating_circuit_party_2_5 = 30
    heating_circuit_party_3 = 31
    heating_circuit_party_3_5 = 32
    heating_circuit_party_4 = 33
    heating_circuit_party_4_5 = 34
    heating_circuit_party_5 = 35
    heating_circuit_party_5_5 = 36
    heating_circuit_party_6 = 37
    heating_circuit_party_6_5 = 38
    heating_circuit_party_7 = 39
    heating_circuit_party_7_5 = 40
    heating_circuit_party_8 = 41
    heating_circuit_party_8_5 = 42
    heating_circuit_party_9 = 43
    heating_circuit_party_9_5 = 44
    heating_circuit_party_10 = 45
    heating_circuit_party_10_5 = 46
    heating_circuit_party_11 = 47
    heating_circuit_party_11_5 = 48
    heating_circuit_party_12 = 49


class HeatingCircuit2PartyPause(IntEnum):
    """Heating circuit2  party and pause mode."""

    heating_circuit2_pause_12 = 1
    heating_circuit2_pause_11_5 = 2
    heating_circuit2_pause_11 = 3
    heating_circuit2_pause_10_5 = 4
    heating_circuit2_pause_10 = 5
    heating_circuit2_pause_9_5 = 6
    heating_circuit2_pause_9 = 7
    heating_circuit2_pause_8_5 = 8
    heating_circuit2_pause_8 = 9
    heating_circuit2_pause_7_5 = 10
    heating_circuit2_pause_7 = 11
    heating_circuit2_pause_6_5 = 12
    heating_circuit2_pause_6 = 13
    heating_circuit2_pause_5_5 = 14
    heating_circuit2_pause_5 = 15
    heating_circuit2_pause_4_5 = 16
    heating_circuit2_pause_4 = 17
    heating_circuit2_pause_3_5 = 18
    heating_circuit2_pause_3 = 19
    heating_circuit2_pause_2_5 = 20
    heating_circuit2_pause_2 = 21
    heating_circuit2_pause_1_5 = 22
    heating_circuit2_pause_1 = 23
    heating_circuit2_pause_0_5 = 24
    heating_circuit2_party_pause_automatic = 25
    heating_circuit2_party_0_5 = 26
    heating_circuit2_party_1 = 27
    heating_circuit2_party_1_5 = 28
    heating_circuit2_party_2 = 29
    heating_circuit2_party_2_5 = 30
    heating_circuit2_party_3 = 31
    heating_circuit2_party_3_5 = 32
    heating_circuit2_party_4 = 33
    heating_circuit2_party_4_5 = 34
    heating_circuit2_party_5 = 35
    heating_circuit2_party_5_5 = 36
    heating_circuit2_party_6 = 37
    heating_circuit2_party_6_5 = 38
    heating_circuit2_party_7 = 39
    heating_circuit2_party_7_5 = 40
    heating_circuit2_party_8 = 41
    heating_circuit2_party_8_5 = 42
    heating_circuit2_party_9 = 43
    heating_circuit2_party_9_5 = 44
    heating_circuit2_party_10 = 45
    heating_circuit2_party_10_5 = 46
    heating_circuit2_party_11 = 47
    heating_circuit2_party_11_5 = 48
    heating_circuit2_party_12 = 49


class DomesticHotWaterPush(IntEnum):
    """Domestic hot water push duration."""

    domestic_hot_water_push_off = 0
    domestic_hot_water_push_5 = 5
    domestic_hot_water_push_10 = 10
    domestic_hot_water_push_15 = 15
    domestic_hot_water_push_20 = 20
    domestic_hot_water_push_25 = 25
    domestic_hot_water_push_30 = 30
    domestic_hot_water_push_35 = 35
    domestic_hot_water_push_40 = 40
    domestic_hot_water_push_45 = 45
    domestic_hot_water_push_50 = 50
    domestic_hot_water_push_55 = 55
    domestic_hot_water_push_60 = 60
    domestic_hot_water_push_65 = 65
    domestic_hot_water_push_70 = 70
    domestic_hot_water_push_75 = 75
    domestic_hot_water_push_80 = 80
    domestic_hot_water_push_85 = 85
    domestic_hot_water_push_90 = 90
    domestic_hot_water_push_95 = 95
    domestic_hot_water_push_100 = 100
    domestic_hot_water_push_105 = 105
    domestic_hot_water_push_110 = 110
    domestic_hot_water_push_115 = 115
    domestic_hot_water_push_120 = 120
    domestic_hot_water_push_125 = 125
    domestic_hot_water_push_130 = 130
    domestic_hot_water_push_135 = 135
    domestic_hot_water_push_140 = 140
    domestic_hot_water_push_145 = 145
    domestic_hot_water_push_150 = 150
    domestic_hot_water_push_155 = 155
    domestic_hot_water_push_160 = 160
    domestic_hot_water_push_165 = 165
    domestic_hot_water_push_170 = 170
    domestic_hot_water_push_175 = 175
    domestic_hot_water_push_180 = 180
    domestic_hot_water_push_185 = 185
    domestic_hot_water_push_190 = 190
    domestic_hot_water_push_195 = 195
    domestic_hot_water_push_200 = 200
    domestic_hot_water_push_205 = 205
    domestic_hot_water_push_210 = 210
    domestic_hot_water_push_215 = 215
    domestic_hot_water_push_220 = 220
    domestic_hot_water_push_225 = 225
    domestic_hot_water_push_230 = 230
    domestic_hot_water_push_235 = 235


class Dummy(IntEnum):
    """Dummy enum."""

    null = 0
    eins = 1
    zwei = 2
    drei = 3
    vier = 4
    fuenf = 5
    sechs = 6
    sieben = 7
    acht = 8
    neun = 9
    zehn = 10
    elf = 11
    zwoelf = 12
    dreizehn = 13
    vierzehn = 14
    fuenfzehn = 15
    sechzehn = 16
    siebzehn = 17
    achtzehn = 18
    neunzehn = 19
    zwanzig = 20
    einundzwanzig = 21
    zweiundzwanzig = 22
    dreiundzwanzig = 23
    vierundzwanzig = 24
    fuenfundzwanzig = 25
    sechsundzwanzig = 26
    siebenundzwanzig = 27
    achtundzwanzig = 28
    neunundzwanzig = 29
    dreissig = 30
    einunddreissig = 31
    zweiunddreissig = 32
    dreiunddreissig = 33
    vierunddreissig = 34
    fuenfunddreissig = 35
    sechsunddreissig = 36
    siebenunddreissig = 37
    achtunddreissig = 38
    neununddreissig = 39
    vierzig = 40
    einundvierzig = 41
    zweiundvierzig = 42
    dreiundvierzig = 43
    vierundvierzig = 44
    fuenfundvierzig = 45
    sechsundvierzig = 46
    siebenundvierzig = 47
    achtundvierzig = 48
    neunundvierzig = 49
    fuenfzig = 50
    einundfuenfzig = 51
    zweiundfuenfzig = 52
    dreiundfuenfzig = 53
    vierundfuenfzig = 54
    fuenfundfuenfzig = 55
    sechsundfuenfzig = 56
    siebenundfuenfzig = 57
    achtundfuenfzig = 58
    neunundfuenfzig = 59
    sechzig = 60
    einundsechzig = 61
    zweiundsechzig = 62
    dreiundsechzig = 63
    vierundsechzig = 64
    fuenfundsechzig = 65
    sechsundsechzig = 66
    siebenundsechzig = 67
    achtundsechzig = 68
    neunundsechzig = 69
    siebzig = 70
    einundsiebzig = 71
    zweiundsiebzig = 72
    dreiundsiebzig = 73
    vierundsiebzig = 74
    fuenfundsiebzig = 75
    sechsundsiebzig = 76
    siebenundsiebzig = 77
    achtundsiebzig = 78
    neunundsiebzig = 79
    achtzig = 80
    einundachtzig = 81
    zweiundachtzig = 82
    dreiundachtzig = 83
    vierundachtzig = 84
    fuenfundachtzig = 85
    sechsundachtzig = 86
    siebenundachtzig = 87
    achtundachtzig = 88
    neunundachtzig = 89
    neunzig = 90
    einundneunzig = 91
    zweiundneunzig = 92
    dreiundneunzig = 93
    vierundneunzig = 94
    fuenfundneunzig = 95
    sechsundneunzig = 96
    siebenundneunzig = 97
    achtundneunzig = 98
    neunundneunzig = 99
    einhundert = 100
    einhunderteins = 101
    einhundertzwei = 102
    einhundertdrei = 103
    einhundertvier = 104
    einhundertfuenf = 105
    einhundertsechs = 106
    einhundertsieben = 107
    einhundertacht = 108
    einhundertneun = 109
    einhundertzehn = 110
    einhundertelf = 111
    einhundertzwoelf = 112
    einhundertdreizehn = 113
    einhundertvierzehn = 114
    einhundertfuenfzehn = 115
    einhundertsechzehn = 116
    einhundertsiebzehn = 117
    einhundertachtzehn = 118
    einhundertneunzehn = 119
    einhundertzwanzig = 120
    einhunderteinundzwanzig = 121
    einhundertzweiundzwanzig = 122
    einhundertdreiundzwanzig = 123
    einhundertvierundzwanzig = 124
    einhundertfuenfundzwanzig = 125
    einhundertsechsundzwanzig = 126
    einhundertsiebenundzwanzig = 127
    einhundertachtundzwanzig = 128
    einhundertneunundzwanzig = 129
    einhundertdreissig = 130
    einhunderteinunddreissig = 131
    einhundertzweiunddreissig = 132
    einhundertdreiunddreissig = 133
    einhundertvierunddreissig = 134
    einhundertfuenfunddreissig = 135
    einhundertsechsunddreissig = 136
    einhundertsiebenunddreissig = 137
    einhundertachtunddreissig = 138
    einhundertneununddreissig = 139
    einhundertvierzig = 140
    einhunderteinundvierzig = 141
    einhundertzweiundvierzig = 142
    einhundertdreiundvierzig = 143
    einhundertvierundvierzig = 144
    einhundertfuenfundvierzig = 145
    einhundertsechsundvierzig = 146
    einhundertsiebenundvierzig = 147
    einhundertachtundvierzig = 148
    einhundertneunundvierzig = 149
    einhundertfuenfzig = 150
    einhunderteinundfuenfzig = 151
    einhundertzweiundfuenfzig = 152
    einhundertdreiundfuenfzig = 153
    einhundertvierundfuenfzig = 154
    einhundertfuenfundfuenfzig = 155
    einhundertsechsundfuenfzig = 156
    einhundertsiebenundfuenfzig = 157
    einhundertachtundfuenfzig = 158
    einhundertneunundfuenfzig = 159
    einhundertsechzig = 160
    einhunderteinundsechzig = 161
    einhundertzweiundsechzig = 162
    einhundertdreiundsechzig = 163
    einhundertvierundsechzig = 164
    einhundertfuenfundsechzig = 165
    einhundertsechsundsechzig = 166
    einhundertsiebenundsechzig = 167
    einhundertachtundsechzig = 168
    einhundertneunundsechzig = 169
    einhundertsiebzig = 170
    einhunderteinundsiebzig = 171
    einhundertzweiundsiebzig = 172
    einhundertdreiundsiebzig = 173
    einhundertvierundsiebzig = 174
    einhundertfuenfundsiebzig = 175
    einhundertsechsundsiebzig = 176
    einhundertsiebenundsiebzig = 177
    einhundertachtundsiebzig = 178
    einhundertneunundsiebzig = 179
    einhundertachtzig = 180
    einhunderteinundachtzig = 181
    einhundertzweiundachtzig = 182
    einhundertdreiundachtzig = 183
    einhundertvierundachtzig = 184
    einhundertfuenfundachtzig = 185
    einhundertsechsundachtzig = 186
    einhundertsiebenundachtzig = 187
    einhundertachtundachtzig = 188
    einhundertneunundachtzig = 189
    einhundertneunzig = 190
    einhunderteinundneunzig = 191
    einhundertzweiundneunzig = 192
    einhundertdreiundneunzig = 193
    einhundertvierundneunzig = 194
    einhundertfuenfundneunzig = 195
    einhundertsechsundneunzig = 196
    einhundertsiebenundneunzig = 197
    einhundertachtundneunzig = 198
    einhundertneunundneunzig = 199
    zweihundert = 200
