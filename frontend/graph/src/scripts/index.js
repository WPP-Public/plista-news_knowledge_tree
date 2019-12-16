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

    // key values for the elements of the json
    networkSeries.dataFields.value = "value";
    networkSeries.dataFields.name = "name";
    networkSeries.dataFields.children = "children";
    networkSeries.nodes.template.label.text = "{name}";
    networkSeries.dataFields.collapsed = "collapsed";

    // html rendering
    //https://www.amcharts.com/docs/v4/tutorials/clickable-links-in-tooltips/
    networkSeries.nodes.template.tooltipHTML = '{name}';
    networkSeries.tooltip.keepTargetHover = true;
    networkSeries.tooltip.label.interactionsEnabled = true;

    // style setting
    networkSeries.nodes.template.fillOpacity = 1;
    networkSeries.minRadius = am4core.percent(2);
    networkSeries.maxRadius = am4core.percent(5);
    networkSeries.fontSize = 10;
    networkSeries.links.template.strokeWidth = 8;
    networkSeries.links.template.strokeOpacity = 0.8;

    // attraction repulsion of the graph
    networkSeries.centerStrength = 2;
    networkSeries.manyBodyStrength = -50;
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