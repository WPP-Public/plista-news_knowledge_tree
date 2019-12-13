// imports
import axios from 'axios';
import '../styles/index.scss';
//import json from '../../../../data/tree_example.json';



am4core.ready(function () {

  // initializing themes
  am4core.useTheme(am4themes_frozen);
//  am4core.useTheme(am4themes_animated);

  // create a bubble chart
  const chart = am4core.create("chartdiv", am4plugins_forceDirected.ForceDirectedTree);
  const networkSeries = chart.series.push(new am4plugins_forceDirected.ForceDirectedSeries());



  const initChart = (data) => {
    // bubble chart data
    chart.data = [data];

    // basic bubble chart options
    networkSeries.dataFields.value = "value";
    networkSeries.dataFields.name = "name";
    networkSeries.dataFields.children = "children";
    networkSeries.nodes.template.tooltipHTML = '{name}'; //https://www.amcharts.com/docs/v4/tutorials/clickable-links-in-tooltips/
    networkSeries.tooltip.keepTargetHover = true;
    networkSeries.tooltip.label.interactionsEnabled = true;
    networkSeries.nodes.template.fillOpacity = 1;
    networkSeries.links.template.strength = 0.8;
    networkSeries.minRadius = am4core.percent(2);
    networkSeries.maxRadius = am4core.percent(8);


    networkSeries.nodes.template.label.text = "{name}";
    networkSeries.fontSize = 10;
    networkSeries.maxLevels = 2;
    networkSeries.links.template.strokeWidth = 8;
    networkSeries.links.template.strokeOpacity = 0.8;
    networkSeries.manyBodyStrength = -15;
    networkSeries.links.template.strength = 2;
    networkSeries.nodes.template.label.hideOversized = true;
  };

    var languageEl = document.getElementById('language');
    var languageElVal = 'en';
    languageEl.addEventListener('change', function() {
        console.log(languageEl.value);
        languageElVal = languageEl.value;
    });

    var countryEl = document.getElementById('country');
    var countryElVal = 'gb';
    countryEl.addEventListener('change', function() {
        console.log(countryEl.value);
        countryElVal = countryEl.value;
    });

    var searchEl = document.getElementById('search');
    var searchElVal = '';
    searchEl.addEventListener('keyup', function() {
        console.log(searchEl.value);
        searchElVal = searchEl.value;
    });

    var fetchBtn = document.getElementById('fetch');
    fetchBtn.addEventListener('click', function() {
        fecthData();
    });



    function fecthData() {
        axios.get(`http://0.0.0.0:5000/get_tree?language=${languageElVal}&country=${countryElVal}`)
        .then(res => {
          console.log(res);
          return res['data'];
        })
        .then(data => {
          initChart(data);
        })
        .catch(function (error) {
          // handle error
          console.log(error);
        });
    }

//    fecthData();

});