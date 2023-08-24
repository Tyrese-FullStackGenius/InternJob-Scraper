import { Component, OnInit } from '@angular/core';
import { getCSSVariableValue } from '../../../../../../kt/_utils';

@Component({
  selector: 'app-chart-app-submitted',
  templateUrl: './chart-app-submitted.component.html',
})
export class ChartAppSubmittedComponent implements OnInit {
  chartOptions: any = {};

  constructor() {}

  ngOnInit(): void {
    this.chartOptions = getChartOptions(350);
  }
}

function getChartOptions(height: number) {
  const labelColor = getCSSVariableValue('--kt-gray-500');
  const borderColor = getCSSVariableValue('--kt-gray-200');
  const baseColor = getCSSVariableValue('--kt-success');
  const secondaryColor = getCSSVariableValue('--kt-success-light');

  return {
    series: [
      {
        name: 'Total',
        data: [8, 9, 15, 9, 10, 12],
      },
      /*{
        name: 'Revenue',
        data: [76, 85, 101, 98, 87, 105],
      },*/
    ],
    chart: {
      fontFamily: 'inherit',
      type: 'area',
      height: height,
      toolbar: {
        show: false,
      },
    },
    plotOptions: {},
    legend: {
      show: false,
    },
    dataLabels: {
      enabled: false,
    },fill: {
      type: 'solid',
      opacity: 1,
    },
    stroke: {
      curve: 'smooth',
      show: true,
      width: 3,
      colors: [baseColor],
    },
    xaxis: {
      categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June'],
      axisBorder: {
        show: false,
      },
      axisTicks: {
        show: false,
      },
      labels: {
        style: {
          colors: labelColor,
          fontSize: '12px',
        },
      },
      crosshairs: {
        position: 'front',
        stroke: {
          color: baseColor,
          width: 1,
          dashArray: 3,
        },
      },
      tooltip: {
        enabled: true,
        formatter: undefined,
        offsetY: 0,
        style: {
          fontSize: '12px',
        },
      },
    },
    yaxis: {
      labels: {
        style: {
          colors: labelColor,
          fontSize: '12px',
        },
      },
    },
    states: {
      normal: {
        filter: {
          type: 'none',
          value: 0,
        },
      },
      hover: {
        filter: {
          type: 'none',
          value: 0,
        },
      },
      active: {
        allowMultipleDataPointsSelection: false,
        filter: {
          type: 'none',
          value: 0,
        },
      },
    },
    tooltip: {
      style: {
        fontSize: '12px',
      },
      y: {
        formatter: function (val: number) {
          return val + ' ';
        },
      },
    },
    colors: [secondaryColor],
    grid: {
      borderColor: borderColor,
      strokeDashArray: 4,
      yaxis: {
        lines: {
          show: true,
        },
      },
    },
    markers: {
      strokeColors: baseColor,
      strokeWidth: 3,
    },
  };
}
