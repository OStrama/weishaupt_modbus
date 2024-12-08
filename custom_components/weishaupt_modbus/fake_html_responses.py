"""HTML Strings as fake responses."""

INFO_WP = """
<!doctype html>
<html lang="en">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="">
    <title>
        WEM Lokal</title>

    <!-- Bootstrap core CSS -->
    <link href="css/bootstrap.css" rel="stylesheet">

    <!-- Custom styles for this template -->
    <link href="css/dashboard.css" rel="stylesheet">

    <link href="css/bootstrap-datepicker3.standalone.css" rel="stylesheet">

    <script src="js/jquery-3.5.1.min.js"></script>
    <script src="js/bootstrap.js"></script>
    <script src="js/Chart.bundle.min.js"></script>
    <script src="js/moment.js"></script>
    <script src="js/bootstrap-datepicker.js"></script>
    <script src="js/bootstrap-datepicker.de.min.js"></script>
    <style>
        .browseobj {
            background-color: lightgrey;
            color: black;
        }

        .activeobj {
            background-color: darkgrey;
        }
    </style>

</head>

<body>
    <nav class="navbar navbar-dark sticky-top bg-dark flex-md-nowrap p-0">
        <a class="navbar-brand col-sm-3 col-md-2 mr-0" href="/home.html">EC-BIBLOCK COM V5.3 Rev. 9</a>
        <ul class="navbar-nav px-3">
            <li class="nav-item text-nowrap">
                <span class="navbar-text">Hallo Mad_One!</span>
            </li>
        </ul>
        <ul class="navbar-nav px-3">
            <li class="nav-item text-nowrap">
                <a class="nav-link" href="logout.html">Ausloggen</a>
            </li>
        </ul>
    </nav>
    <div class="container-fluid">
        <div class="row">
            <nav class="col-md-2 d-none d-md-block bg-light sidebar mt-5">
                <div class="sidebar-sticky">
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link" href="/home.html">
                                Dashboard </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/monitor.html">
                                Monitor </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link active" href="/settings_export.html">
                                Profimodus </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/settings.html">
                                Einstellungen </a>
                        </li>
                    </ul>
                </div>
            </nav>
            <main role="main" class="col-md-9 ml-sm-auto col-lg-10 pt-3 px-4">
                <div
                    class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 border-bottom">
                    <h1 class="h2">Profimodus</h1>
                </div>
                <div class="container mx-0">
                    <div class="row">
                        <div class="col-3">
                            <div class="nav flex-column nav-pills" role="tablist" aria-orientation="vertical"><a
                                    class="nav-link browseobj activeobj"
                                    href="/settings_export.html?stack=0C00000100000000008000F9AF010002000301"
                                    role="tab">
                                    <h5>Info</h5>

                                </a>
                                <a class="nav-link browseobj"
                                    href="/settings_export.html?stack=0600000100000000008000F9AF010011000301"
                                    role="tab">
                                    <h5>Systembetriebsart</h5>

                                </a>
                                <a class="nav-link browseobj"
                                    href="/settings_export.html?stack=3200000100000000008000F9AF010002000301"
                                    role="tab">
                                    <h5>Heizkreis 1</h5>

                                </a>
                                <a class="nav-link browseobj"
                                    href="/settings_export.html?stack=3300000100000000008000F9AF010002000301"
                                    role="tab">
                                    <h5>Heizkreis 2</h5>

                                </a>
                                <a class="nav-link browseobj"
                                    href="/settings_export.html?stack=4600000100000000008000F9AF010002000301"
                                    role="tab">
                                    <h5>Warmwasser</h5>

                                </a>
                                <a class="nav-link browseobj"
                                    href="/settings_export.html?stack=6400000100000000008000F9AF010002000301"
                                    role="tab">
                                    <h5>Wärmepumpe</h5>

                                </a>
                                <a class="nav-link browseobj"
                                    href="/settings_export.html?stack=6500000100000000008000F9AF010002000301"
                                    role="tab">
                                    <h5>2. WEZ</h5>

                                </a>
                                <a class="nav-link browseobj"
                                    href="/settings_export.html?stack=BE00000100000000008000F9AF010002000301"
                                    role="tab">
                                    <h5>Eingänge</h5>

                                </a>
                                <a class="nav-link browseobj"
                                    href="/settings_export.html?stack=C200000100000000008000F9AF010002000301"
                                    role="tab">
                                    <h5>Ausgänge</h5>

                                </a>
                                <a class="nav-link browseobj"
                                    href="/settings_export.html?stack=0100000100000000008000F9AF010002000301"
                                    role="tab">
                                    <h5>Einstellungen</h5>

                                </a>
                                <a class="nav-link browseobj"
                                    href="/settings_export.html?stack=C300000100000000008000F9AF010002000301"
                                    role="tab">
                                    <h5>Fehlerspeicher</h5>

                                </a>
                                <a class="nav-link browseobj"
                                    href="/settings_export.html?stack=5800000100000000008000F9AF010002000301"
                                    role="tab">
                                    <h5>Energiemanagement</h5>

                                </a>
                            </div>
                        </div>
                        <div class="col-3">
                            <div class="nav flex-column nav-pills" role="tablist" aria-orientation="vertical"><a
                                    class="nav-link browseobj"
                                    href="/settings_export.html?stack=0C00000100000000008000F9AF010002000301,0C000C1900000000000000F9AF020003000401"
                                    role="tab">
                                    <h5>Heizkreis 1</h5>

                                </a>
                                <a class="nav-link browseobj activeobj"
                                    href="/settings_export.html?stack=0C00000100000000008000F9AF010002000301,0C000C2200000000000000F9AF020003000401"
                                    role="tab">
                                    <h5>Wärmepumpe</h5>

                                </a>
                                <a class="nav-link browseobj"
                                    href="/settings_export.html?stack=0C00000100000000008000F9AF010002000301,0C000C2300000000000000F9AF020003000401"
                                    role="tab">
                                    <h5>2. WEZ</h5>

                                </a>
                                <a class="nav-link browseobj"
                                    href="/settings_export.html?stack=0C00000100000000008000F9AF010002000301,0C000C2700000000000000F9AF020003000401"
                                    role="tab">
                                    <h5>Statistik</h5>

                                </a>
                            </div>
                        </div>
                        <div class="col-3">
                            <div class="nav flex-column nav-pills" role="tablist" aria-orientation="vertical">
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Betrieb</h5>
                                    Heizbetrieb
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Störmeldung</h5>
                                    --
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Warmwassertemperatur</h5>
                                    44.5 °C
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Leistungsanforderung</h5>
                                    87 %
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Solltemperatur</h5>
                                    33.5 °C
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Schaltdifferenz dynamisch</h5>
                                    4.5 K
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Vorlauftemperatur</h5>
                                    33.0 °C
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Rücklauftemperatur</h5>
                                    28.5 °C
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Drehzahl Pumpe M1</h5>
                                    90 %
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Volumenstrom</h5>
                                    1.6m3/h
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Stellung Umschaltventil</h5>
                                    Heizkreis
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Version WWP-SG</h5>
                                    V3.0
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Version WWP-EC WBB</h5>
                                    V5.3
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Soll Leistung</h5>
                                    7.7 KW
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Ist Leistung</h5>
                                    7.7 KW
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Expansionsventil AG Eintr</h5>
                                    9.5 °C
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Luftansaugtemperatur</h5>
                                    -3.5 °C
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Wärmetauscher AG Austrit</h5>
                                    -4.0 °C
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Verdichtersauggastemp.</h5>
                                    3.0 °C
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>EVI Sauggastemperatur</h5>
                                    14.0 °C
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Kältemittel IG Austritt</h5>
                                    12.0 °C
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Ölsumpftemperatur</h5>
                                    46.5 °C
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Druckgastemperatur</h5>
                                    82.5 °C
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Niederdruck</h5>
                                    4.3 BAR
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Verdampfungstemperatur</h5>
                                    -11.5 °C
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Hochdruck</h5>
                                    19.6 BAR
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Kondensationstemperatur</h5>
                                    33.5 °C
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Mitteldruck</h5>
                                    8.4 BAR
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Sättigungstemperatur EVI</h5>
                                    6.0 °C
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Überhitzung Heizen</h5>
                                    7.5 K
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Öffnungsgrad EXV Heizen</h5>
                                    17 %
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Überhitzung Verdichter</h5>
                                    15.0 K
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Öffnungsgrad EXV Kühlen</h5>
                                    0 %
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Überhitzung EVI</h5>
                                    8.0 K
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Öffnungsgrad EVI</h5>
                                    12 %
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Betriebsstd. Verdichter</h5>
                                    1099 h
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Schaltspiele Verdichter</h5>
                                    507
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Schaltspiele Abtauen</h5>
                                    128
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Verdichter</h5>
                                    6075 rpm
                                </div>
                                <div class="nav-link browseobj" role="tab">
                                    <h5>Außengerät Variante</h5>
                                    RMHA-10
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="container mx-0 mt-1">
                    <form action="/settings_export.html" method="GET">
                        <div class="row"><label for="access_code">Zugriffscode verändern</label>
                        </div>
                        <div class="row"><input type="text" maxlength="4" required="true" id="access_code"
                                name="access_code"></div>
                        <div class="row mt-1"><button type="submit" class="btn btn-sm btn-success">Anwenden</button>
            </main>

        </div>
    </div>

</body>

</html>
"""


INFO_HK1 = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="">
    <title>
WEM Lokal</title>

    <!-- Bootstrap core CSS -->
    <link href="css/bootstrap.css" rel="stylesheet">

    <!-- Custom styles for this template -->
    <link href="css/dashboard.css" rel="stylesheet">

    <link href="css/bootstrap-datepicker3.standalone.css" rel="stylesheet">

    <script src="js/jquery-3.5.1.min.js"></script>
    <script src="js/bootstrap.js"></script>
    <script src="js/Chart.bundle.min.js"></script>
    <script src="js/moment.js"></script>
    <script src="js/bootstrap-datepicker.js"></script>
    <script src="js/bootstrap-datepicker.de.min.js"></script>
    <style>
    .browseobj {
      background-color: lightgrey;
      color: black;
    }
    .activeobj {
      background-color: darkgrey;
    }
    </style>

  </head>

  <body>
    <nav class="navbar navbar-dark sticky-top bg-dark flex-md-nowrap p-0">
			<a class="navbar-brand col-sm-3 col-md-2 mr-0" href="/home.html">EC-BIBLOCK COM V5.3 Rev. 9</a>
      <ul class="navbar-nav px-3">
        <li class="nav-item text-nowrap">
<span class="navbar-text">Hallo Mad_One!</span>				</li>
			</ul>
      <ul class="navbar-nav px-3">
        <li class="nav-item text-nowrap">
		     <a class="nav-link" href="logout.html">Ausloggen</a>
				</li>
			</ul>
		</nav>
	  <div class="container-fluid">
		<div class="row">
<nav class="col-md-2 d-none d-md-block bg-light sidebar mt-5">
  <div class="sidebar-sticky">
    <ul class="nav flex-column">
      <li class="nav-item">
        <a class="nav-link" href="/home.html">
Dashboard        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="/monitor.html">
Monitor        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link active" href="/settings_export.html">
Profimodus        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="/settings.html">
Einstellungen        </a>
      </li>
    </ul>
  </div>
</nav>
<main role="main" class="col-md-9 ml-sm-auto col-lg-10 pt-3 px-4">
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 border-bottom">
<h1 class="h2">Profimodus</h1>
</div>
<div class="container mx-0"><div class="row">
<div class="col-3">
<div class="nav flex-column nav-pills" role="tablist" aria-orientation="vertical"><a class="nav-link browseobj activeobj" href="/settings_export.html?stack=0C00000100000000008000F9AF010002000301" role="tab">
<h5>Info</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=0600000100000000008000F9AF010011000301" role="tab">
<h5>Systembetriebsart</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=3200000100000000008000F9AF010002000301" role="tab">
<h5>Heizkreis 1</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=3300000100000000008000F9AF010002000301" role="tab">
<h5>Heizkreis 2</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=4600000100000000008000F9AF010002000301" role="tab">
<h5>Warmwasser</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=6400000100000000008000F9AF010002000301" role="tab">
<h5>Wärmepumpe</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=6500000100000000008000F9AF010002000301" role="tab">
<h5>2. WEZ</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=BE00000100000000008000F9AF010002000301" role="tab">
<h5>Eingänge</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=C200000100000000008000F9AF010002000301" role="tab">
<h5>Ausgänge</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=0100000100000000008000F9AF010002000301" role="tab">
<h5>Einstellungen</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=C300000100000000008000F9AF010002000301" role="tab">
<h5>Fehlerspeicher</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=5800000100000000008000F9AF010002000301" role="tab">
<h5>Energiemanagement</h5>

</a>
</div></div>
<div class="col-3">
<div class="nav flex-column nav-pills" role="tablist" aria-orientation="vertical"><a class="nav-link browseobj activeobj" href="/settings_export.html?stack=0C00000100000000008000F9AF010002000301,0C000C1900000000000000F9AF020003000401" role="tab">
<h5>Heizkreis 1</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=0C00000100000000008000F9AF010002000301,0C000C2200000000000000F9AF020003000401" role="tab">
<h5>Wärmepumpe</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=0C00000100000000008000F9AF010002000301,0C000C2300000000000000F9AF020003000401" role="tab">
<h5>2. WEZ</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=0C00000100000000008000F9AF010002000301,0C000C2700000000000000F9AF020003000401" role="tab">
<h5>Statistik</h5>

</a>
</div></div>
<div class="col-3">
<div class="nav flex-column nav-pills" role="tablist" aria-orientation="vertical"><div class="nav-link browseobj" role="tab">
<h5>Außentemperatur</h5>
3.0 °C
</div>
<div class="nav-link browseobj" role="tab">
<h5>AT Mittelwert</h5>
3.5 °C
</div>
<div class="nav-link browseobj" role="tab">
<h5>AT Langzeitwert</h5>
4.5 °C
</div>
<div class="nav-link browseobj" role="tab">
<h5>Raumsolltemperatur</h5>
23.0 °C
</div>
<div class="nav-link browseobj" role="tab">
<h5>Vorlaufsolltemperatur</h5>
30.5 °C
</div>
<div class="nav-link browseobj" role="tab">
<h5>Vorlauftemperatur</h5>
31.0 °C
</div>
</div></div>
</div></div><div class="container mx-0 mt-1"><form action="/settings_export.html" method="GET">
<div class="row"><label for="access_code">Zugriffscode verändern</label>
</div><div class="row"><input type="text" maxlength="4" required="true" id="access_code" name="access_code"
></div><div class="row mt-1"><button type="submit" class="btn btn-sm btn-success">Anwenden</button></main>

      </div>
    </div>

  </body>
</html>

"""


INFO_2WEZ = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="">
    <title>
WEM Lokal</title>

    <!-- Bootstrap core CSS -->
    <link href="css/bootstrap.css" rel="stylesheet">

    <!-- Custom styles for this template -->
    <link href="css/dashboard.css" rel="stylesheet">

    <link href="css/bootstrap-datepicker3.standalone.css" rel="stylesheet">

    <script src="js/jquery-3.5.1.min.js"></script>
    <script src="js/bootstrap.js"></script>
    <script src="js/Chart.bundle.min.js"></script>
    <script src="js/moment.js"></script>
    <script src="js/bootstrap-datepicker.js"></script>
    <script src="js/bootstrap-datepicker.de.min.js"></script>
    <style>
    .browseobj {
      background-color: lightgrey;
      color: black;
    }
    .activeobj {
      background-color: darkgrey;
    }
    </style>

  </head>

  <body>
    <nav class="navbar navbar-dark sticky-top bg-dark flex-md-nowrap p-0">
			<a class="navbar-brand col-sm-3 col-md-2 mr-0" href="/home.html">EC-BIBLOCK COM V5.3 Rev. 9</a>
      <ul class="navbar-nav px-3">
        <li class="nav-item text-nowrap">
<span class="navbar-text">Hallo Mad_One!</span>				</li>
			</ul>
      <ul class="navbar-nav px-3">
        <li class="nav-item text-nowrap">
		     <a class="nav-link" href="logout.html">Ausloggen</a>
				</li>
			</ul>
		</nav>
	  <div class="container-fluid">
		<div class="row">
<nav class="col-md-2 d-none d-md-block bg-light sidebar mt-5">
  <div class="sidebar-sticky">
    <ul class="nav flex-column">
      <li class="nav-item">
        <a class="nav-link" href="/home.html">
Dashboard        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="/monitor.html">
Monitor        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link active" href="/settings_export.html">
Profimodus        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="/settings.html">
Einstellungen        </a>
      </li>
    </ul>
  </div>
</nav>
<main role="main" class="col-md-9 ml-sm-auto col-lg-10 pt-3 px-4">
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 border-bottom">
<h1 class="h2">Profimodus</h1>
</div>
<div class="container mx-0"><div class="row">
<div class="col-3">
<div class="nav flex-column nav-pills" role="tablist" aria-orientation="vertical"><a class="nav-link browseobj activeobj" href="/settings_export.html?stack=0C00000100000000008000F9AF010002000301" role="tab">
<h5>Info</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=0600000100000000008000F9AF010011000301" role="tab">
<h5>Systembetriebsart</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=3200000100000000008000F9AF010002000301" role="tab">
<h5>Heizkreis 1</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=3300000100000000008000F9AF010002000301" role="tab">
<h5>Heizkreis 2</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=4600000100000000008000F9AF010002000301" role="tab">
<h5>Warmwasser</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=6400000100000000008000F9AF010002000301" role="tab">
<h5>Wärmepumpe</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=6500000100000000008000F9AF010002000301" role="tab">
<h5>2. WEZ</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=BE00000100000000008000F9AF010002000301" role="tab">
<h5>Eingänge</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=C200000100000000008000F9AF010002000301" role="tab">
<h5>Ausgänge</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=0100000100000000008000F9AF010002000301" role="tab">
<h5>Einstellungen</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=C300000100000000008000F9AF010002000301" role="tab">
<h5>Fehlerspeicher</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=5800000100000000008000F9AF010002000301" role="tab">
<h5>Energiemanagement</h5>

</a>
</div></div>
<div class="col-3">
<div class="nav flex-column nav-pills" role="tablist" aria-orientation="vertical"><a class="nav-link browseobj" href="/settings_export.html?stack=0C00000100000000008000F9AF010002000301,0C000C1900000000000000F9AF020003000401" role="tab">
<h5>Heizkreis 1</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=0C00000100000000008000F9AF010002000301,0C000C2200000000000000F9AF020003000401" role="tab">
<h5>Wärmepumpe</h5>

</a>
<a class="nav-link browseobj activeobj" href="/settings_export.html?stack=0C00000100000000008000F9AF010002000301,0C000C2300000000000000F9AF020003000401" role="tab">
<h5>2. WEZ</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=0C00000100000000008000F9AF010002000301,0C000C2700000000000000F9AF020003000401" role="tab">
<h5>Statistik</h5>

</a>
</div></div>
<div class="col-3">
<div class="nav flex-column nav-pills" role="tablist" aria-orientation="vertical"><div class="nav-link browseobj" role="tab">
<h5>Status</h5>
0
</div>
<div class="nav-link browseobj" role="tab">
<h5>Status E-Heizung 1</h5>
Aus
</div>
<div class="nav-link browseobj" role="tab">
<h5>Status E-Heizung 2</h5>
Aus
</div>
<div class="nav-link browseobj" role="tab">
<h5>Betriebsstunden E1</h5>
5 h
</div>
<div class="nav-link browseobj" role="tab">
<h5>Betriebsstunden E2</h5>
0 h
</div>
<div class="nav-link browseobj" role="tab">
<h5>Schaltspiele E1</h5>
8
</div>
<div class="nav-link browseobj" role="tab">
<h5>Schaltspiele E2</h5>
0
</div>
</div></div>
</div></div><div class="container mx-0 mt-1"><form action="/settings_export.html" method="GET">
<div class="row"><label for="access_code">Zugriffscode verändern</label>
</div><div class="row"><input type="text" maxlength="4" required="true" id="access_code" name="access_code"
></div><div class="row mt-1"><button type="submit" class="btn btn-sm btn-success">Anwenden</button></main>

      </div>
    </div>

  </body>
</html>

"""

INFO_STATISTIK = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="">
    <title>
WEM Lokal</title>

    <!-- Bootstrap core CSS -->
    <link href="css/bootstrap.css" rel="stylesheet">

    <!-- Custom styles for this template -->
    <link href="css/dashboard.css" rel="stylesheet">

    <link href="css/bootstrap-datepicker3.standalone.css" rel="stylesheet">

    <script src="js/jquery-3.5.1.min.js"></script>
    <script src="js/bootstrap.js"></script>
    <script src="js/Chart.bundle.min.js"></script>
    <script src="js/moment.js"></script>
    <script src="js/bootstrap-datepicker.js"></script>
    <script src="js/bootstrap-datepicker.de.min.js"></script>
    <style>
    .browseobj {
      background-color: lightgrey;
      color: black;
    }
    .activeobj {
      background-color: darkgrey;
    }
    </style>

  </head>

  <body>
    <nav class="navbar navbar-dark sticky-top bg-dark flex-md-nowrap p-0">
			<a class="navbar-brand col-sm-3 col-md-2 mr-0" href="/home.html">EC-BIBLOCK COM V5.3 Rev. 9</a>
      <ul class="navbar-nav px-3">
        <li class="nav-item text-nowrap">
<span class="navbar-text">Hallo Mad_One!</span>				</li>
			</ul>
      <ul class="navbar-nav px-3">
        <li class="nav-item text-nowrap">
		     <a class="nav-link" href="logout.html">Ausloggen</a>
				</li>
			</ul>
		</nav>
	  <div class="container-fluid">
		<div class="row">
<nav class="col-md-2 d-none d-md-block bg-light sidebar mt-5">
  <div class="sidebar-sticky">
    <ul class="nav flex-column">
      <li class="nav-item">
        <a class="nav-link" href="/home.html">
Dashboard        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="/monitor.html">
Monitor        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link active" href="/settings_export.html">
Profimodus        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="/settings.html">
Einstellungen        </a>
      </li>
    </ul>
  </div>
</nav>
<main role="main" class="col-md-9 ml-sm-auto col-lg-10 pt-3 px-4">
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pb-2 mb-3 border-bottom">
<h1 class="h2">Profimodus</h1>
</div>
<div class="container mx-0"><div class="row">
<div class="col-3">
<div class="nav flex-column nav-pills" role="tablist" aria-orientation="vertical"><a class="nav-link browseobj activeobj" href="/settings_export.html?stack=0C00000100000000008000F9AF010002000301" role="tab">
<h5>Info</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=0600000100000000008000F9AF010011000301" role="tab">
<h5>Systembetriebsart</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=3200000100000000008000F9AF010002000301" role="tab">
<h5>Heizkreis 1</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=3300000100000000008000F9AF010002000301" role="tab">
<h5>Heizkreis 2</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=4600000100000000008000F9AF010002000301" role="tab">
<h5>Warmwasser</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=6400000100000000008000F9AF010002000301" role="tab">
<h5>Wärmepumpe</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=6500000100000000008000F9AF010002000301" role="tab">
<h5>2. WEZ</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=BE00000100000000008000F9AF010002000301" role="tab">
<h5>Eingänge</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=C200000100000000008000F9AF010002000301" role="tab">
<h5>Ausgänge</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=0100000100000000008000F9AF010002000301" role="tab">
<h5>Einstellungen</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=C300000100000000008000F9AF010002000301" role="tab">
<h5>Fehlerspeicher</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=5800000100000000008000F9AF010002000301" role="tab">
<h5>Energiemanagement</h5>

</a>
</div></div>
<div class="col-3">
<div class="nav flex-column nav-pills" role="tablist" aria-orientation="vertical"><a class="nav-link browseobj" href="/settings_export.html?stack=0C00000100000000008000F9AF010002000301,0C000C1900000000000000F9AF020003000401" role="tab">
<h5>Heizkreis 1</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=0C00000100000000008000F9AF010002000301,0C000C2200000000000000F9AF020003000401" role="tab">
<h5>Wärmepumpe</h5>

</a>
<a class="nav-link browseobj" href="/settings_export.html?stack=0C00000100000000008000F9AF010002000301,0C000C2300000000000000F9AF020003000401" role="tab">
<h5>2. WEZ</h5>

</a>
<a class="nav-link browseobj activeobj" href="/settings_export.html?stack=0C00000100000000008000F9AF010002000301,0C000C2700000000000000F9AF020003000401" role="tab">
<h5>Statistik</h5>

</a>
</div></div>
<div class="col-3">
<div class="nav flex-column nav-pills" role="tablist" aria-orientation="vertical"><div class="nav-link browseobj" role="tab">
<h5>th. Energie Heizen Tag</h5>
77.721 KWh
</div>
<div class="nav-link browseobj" role="tab">
<h5>th. Energie WW Tag</h5>
9.059 KWh
</div>
<div class="nav-link browseobj" role="tab">
<h5>th. Energie gesamt Tag</h5>
86.781 KWh
</div>
<div class="nav-link browseobj" role="tab">
<h5>elektrische Energie Tag</h5>
21.310 KWh
</div>
<div class="nav-link browseobj" role="tab">
<h5>th. Energie Heizen Monat</h5>
365.165 KWh
</div>
<div class="nav-link browseobj" role="tab">
<h5>th. Energie WW Monat</h5>
51.765 KWh
</div>
<div class="nav-link browseobj" role="tab">
<h5>th. Energie gesamt Monat</h5>
416.931 KWh
</div>
<div class="nav-link browseobj" role="tab">
<h5>elektrische Energie Monat</h5>
112.837 KWh
</div>
<div class="nav-link browseobj" role="tab">
<h5>th. Energie Heizen Jahr</h5>
3706.305 KWh
</div>
<div class="nav-link browseobj" role="tab">
<h5>th. Energie WW Jahr</h5>
1594.536 KWh
</div>
<div class="nav-link browseobj" role="tab">
<h5>th. Energie gesamt Jahr</h5>
5300.841 KWh
</div>
<div class="nav-link browseobj" role="tab">
<h5>elektrische Energie Jahr</h5>
1293.069 KWh
</div>
</div></div>
</div></div><div class="container mx-0 mt-1"><form action="/settings_export.html" method="GET">
<div class="row"><label for="access_code">Zugriffscode verändern</label>
</div><div class="row"><input type="text" maxlength="4" required="true" id="access_code" name="access_code"
></div><div class="row mt-1"><button type="submit" class="btn btn-sm btn-success">Anwenden</button></main>

      </div>
    </div>

  </body>
</html>

"""
