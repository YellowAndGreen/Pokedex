<template>
  <VRow class="py-5 match-height">
    <VCol cols="12" md="8" sm="6" class="border-e">
      <div class="pe-3">
        <h5 class="text-h5 text-high-emphasis mb-1">
          Welcome back 👋🏻
        </h5>
        <div class="text-wrap text-medium-emphasis mb-4" style="max-inline-size: 400px;">
          Your progress this week is Awesome. let's keep it up and get a lot of points reward!
        </div>
        <div class="d-flex justify-space-between flex-wrap gap-6 flex-column flex-md-row">
          <div>
            <div class="d-flex">
              <VAvatar color="primary" rounded variant="tonal" class="text-primary me-4"
                style="width: 54px; height: 54px;">
                <VIcon size="32" icon="ri-time-line" />
              </VAvatar>
              <div>
                <h6 class="text-h6 text-medium-emphasis">
                  2025活跃天数
                </h6>
                <h4 class="text-h4 font-weight-medium text-primary">
                  43天
                </h4>
              </div>
            </div>
          </div>
          <div>
            <div class="d-flex">
              <VAvatar color="info" rounded variant="tonal" class="text-primary me-4"
                style="width: 54px; height: 54px;">
                <VIcon size="32" icon="ri-test-tube-line" />
              </VAvatar>
              <div>
                <h6 class="text-h6 text-medium-emphasis">
                  总鸟种数
                </h6>
                <h4 class="text-h4 font-weight-medium text-info">
                  282
                </h4>
              </div>
            </div>
          </div>
          <div>
            <div class="d-flex">
              <VAvatar color="warning" rounded variant="tonal" class="text-primary me-4"
                style="width: 54px; height: 54px;">
                <VIcon size="32" icon="ri-award-line" />
              </VAvatar>
              <div>
                <h6 class="text-h6 text-medium-emphasis">
                  报告数量
                </h6>
                <h4 class="text-h4 font-weight-medium text-warning">
                  65
                </h4>
              </div>
            </div>
          </div>
        </div>
      </div>
    </VCol>
    <VCol cols="12" md="4" sm="6">
      <div class="d-flex justify-space-between align-center">
        <div class="d-flex flex-column ps-3">
          <h5 class="text-h5 mb-1 text-no-wrap">
            Time Spending
          </h5>
          <div class="mb-6 text-body-1">
            Weekly Report
          </div>
          <h4 class="text-h4 mb-2">
            231<span class="text-medium-emphasis">h</span> 14<span class="text-medium-emphasis">m</span>
          </h4>
          <div>
            <VChip color="success" density="default" label size="small" variant="tonal">
              +18.4%
            </VChip>
          </div>
        </div>
        <div>
          <!-- Placeholder for Donut Chart -->
          <div
            style="min-height: 132.8px; width: 150px; border: 1px dashed #ccc; display: flex; align-items: center; justify-content: center;">
            Donut Chart
          </div>
        </div>
      </div>
    </VCol>
  </VRow>

  <!-- New Row for Shipment Statistics and Transactions -->
  <VRow class="mt-6" match-height>
    <!-- Shipment Statistics Card -->
    <VCol cols="12" md="8">
      <VCard>
        <VCardItem>
          <VCardTitle>Shipment statistics</VCardTitle>
          <VCardSubtitle>Total number of deliveries 23.8k</VCardSubtitle>
          <template #append>
            <div class="v-btn-group v-btn-group--divided v-theme--light v-btn-group--density-compact">
              <VBtn variant="outlined" style="height: auto;" color="primary">
                January
              </VBtn>
              <VBtn variant="outlined" style="height: auto;" color="primary" icon>
                <VIcon icon="ri-arrow-down-s-line" />
              </VBtn>
            </div>
          </template>
        </VCardItem>
        <VCardText>
          <VueApexCharts type="bar" :options="shipmentChartOptions" :series="shipmentChartSeries" height="320" />
        </VCardText>
      </VCard>
    </VCol>

    <!-- New Cards Column -->
    <VCol cols="12" md="4">
      <div class="v-col-md-12 v-col-lg-12 v-col-12">
        <div class="v-card v-theme--light v-card--density-default v-card--variant-elevated"
          style="background-color: rgb(22, 177, 255); color: rgb(255, 255, 255); caret-color: rgb(255, 255, 255);">
          <!---->
          <div class="v-card__loader">
            <div class="v-progress-linear v-theme--light v-locale--is-ltr" role="progressbar" aria-hidden="true"
              aria-valuemin="0" aria-valuemax="100" style="top: 0px; height: 0px; --v-progress-linear-height: 2px;">
              <!---->
              <div class="v-progress-linear__background bg-primary"></div>
              <div class="v-progress-linear__buffer bg-primary" style="width: 0%;"></div>
              <div class="v-progress-linear__indeterminate">
                <div class="v-progress-linear__indeterminate long bg-primary"></div>
                <div class="v-progress-linear__indeterminate short bg-primary"></div>
              </div><!---->
            </div>
          </div><!----><!---->
          <div class="v-card-item">
            <div class="v-card-item__prepend"><i class="ri-twitter-line v-icon notranslate v-theme--light text-white"
                aria-hidden="true" style="font-size: 1.9rem; height: 1.9rem; width: 1.9rem;"></i></div>
            <div class="v-card-item__content"><!----><!---->
              <div class="v-card-title text-white">Twitter Card</div>
            </div><!---->
          </div>
          <div class="v-card-text">
            <p class="clamp-text text-white mb-0">"Turns out semicolon-less style is easier and safer in TS because most
              gotcha edge cases are type invalid as well."</p>
          </div>
          <div class="v-card-text d-flex justify-space-between align-center flex-wrap">
            <div class="text-no-wrap">
              <div class="v-avatar v-theme--light v-avatar--density-default v-avatar--variant-flat"
                style="width: 34px; height: 34px;">
                <div class="v-responsive v-img" aria-label="">
                  <div class="v-responsive__sizer" style="padding-bottom: 100%;"></div><img
                    class="v-img__img v-img__img--cover" src="https://sns-avatar-qc.xhscdn.com/avatar/1040g2jo31esupog4me605ogjm7g40vt2421qqeg?imageView2/2/w/360/format/webp" alt="avatar"
                    style=""><!----><!----><!----><!----><!---->
                </div><!----><span class="v-avatar__underlay"></span>
              </div><span class="text-white ms-2">Mary Vaughn</span>
            </div>
            <div class="d-flex align-center"><button type="button"
                class="v-btn v-btn--icon v-theme--light text-white v-btn--density-default v-btn--size-default v-btn--variant-text me-1"><span
                  class="v-btn__overlay"></span><span class="v-btn__underlay"></span><!----><span class="v-btn__content"
                  data-no-activator=""><i class="ri-heart-fill v-icon notranslate v-theme--light v-icon--size-default"
                    aria-hidden="true"></i></span><!----><!----></button><span
                class="text-body-2 text-white me-4">1.2k</span><button type="button"
                class="v-btn v-btn--icon v-theme--light text-white v-btn--density-default v-btn--size-default v-btn--variant-text me-1"><span
                  class="v-btn__overlay"></span><span class="v-btn__underlay"></span><!----><span class="v-btn__content"
                  data-no-activator=""><i class="ri-share-line v-icon notranslate v-theme--light v-icon--size-default"
                    aria-hidden="true"></i></span><!----><!----></button><span class="text-body-2 text-white">80</span>
            </div>
          </div><!----><!----><span class="v-card__underlay"></span>
        </div>
      </div>
      <div class="v-col-md-12 v-col-lg-12 v-col-12">
        <div class="v-card v-theme--light v-card--density-default v-card--variant-elevated"
          style="background-color: rgb(59, 89, 152); color: rgb(255, 255, 255); caret-color: rgb(255, 255, 255);">
          <!---->
          <div class="v-card__loader">
            <div class="v-progress-linear v-theme--light v-locale--is-ltr" role="progressbar" aria-hidden="true"
              aria-valuemin="0" aria-valuemax="100" style="top: 0px; height: 0px; --v-progress-linear-height: 2px;">
              <!---->
              <div class="v-progress-linear__background bg-primary"></div>
              <div class="v-progress-linear__buffer bg-primary" style="width: 0%;"></div>
              <div class="v-progress-linear__indeterminate">
                <div class="v-progress-linear__indeterminate long bg-primary"></div>
                <div class="v-progress-linear__indeterminate short bg-primary"></div>
              </div><!---->
            </div>
          </div><!----><!---->
          <div class="v-card-item">
            <div class="v-card-item__prepend"><i class="ri-facebook-circle-line v-icon notranslate v-theme--light text-white" aria-hidden="true" style="font-size: 1.9rem; height: 1.9rem; width: 1.9rem;"></i></div>
            <div class="v-card-item__content"><!----><!---->
              <div class="v-card-title text-white">Twitter Card</div>
            </div><!---->
          </div>
          <div class="v-card-text">
            <p class="clamp-text text-white mb-0">"Turns out semicolon-less style is easier and safer in TS because most
              gotcha edge cases are type invalid as well."</p>
          </div>
          <div class="v-card-text d-flex justify-space-between align-center flex-wrap">
            <div class="text-no-wrap">
              <div class="v-avatar v-theme--light v-avatar--density-default v-avatar--variant-flat"
                style="width: 34px; height: 34px;">
                <div class="v-responsive v-img" aria-label="">
                  <div class="v-responsive__sizer" style="padding-bottom: 100%;"></div><img
                    class="v-img__img v-img__img--cover" src="https://sns-avatar-qc.xhscdn.com/avatar/1040g2jo31esupog4me605ogjm7g40vt2421qqeg?imageView2/2/w/360/format/webp" alt="avatar"
                    style=""><!----><!----><!----><!----><!---->
                </div><!----><span class="v-avatar__underlay"></span>
              </div><span class="text-white ms-2">Mary Vaughn</span>
            </div>
            <div class="d-flex align-center"><button type="button"
                class="v-btn v-btn--icon v-theme--light text-white v-btn--density-default v-btn--size-default v-btn--variant-text me-1"><span
                  class="v-btn__overlay"></span><span class="v-btn__underlay"></span><!----><span class="v-btn__content"
                  data-no-activator=""><i class="ri-heart-fill v-icon notranslate v-theme--light v-icon--size-default"
                    aria-hidden="true"></i></span><!----><!----></button><span
                class="text-body-2 text-white me-4">1.2k</span><button type="button"
                class="v-btn v-btn--icon v-theme--light text-white v-btn--density-default v-btn--size-default v-btn--variant-text me-1"><span
                  class="v-btn__overlay"></span><span class="v-btn__underlay"></span><!----><span class="v-btn__content"
                  data-no-activator=""><i class="ri-share-line v-icon notranslate v-theme--light v-icon--size-default"
                    aria-hidden="true"></i></span><!----><!----></button><span class="text-body-2 text-white">80</span>
            </div>
          </div><!----><!----><span class="v-card__underlay"></span>
        </div>
      </div>

    </VCol>
  </VRow>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useTheme } from 'vuetify'
import { hexToRgb } from '@layouts/utils'

const vuetifyTheme = useTheme()

const statisticsData = [
  {
    title: '2025出勤时间',
    value: '42',
    icon: 'ri-car-line',
    color: 'primary',
    change: '18.2%',
  },
  {
    title: '2025鸟种数',
    value: '8',
    icon: 'ri-alert-line',
    color: 'warning',
    change: '-8.7%',
  },
  {
    title: '观鸟记录中心',
    value: '27',
    icon: 'ri-stackshare-line',
    color: 'error',
    change: '4.3%',
  },
  {
    title: '报告数量',
    value: '13',
    icon: 'ri-timer-line',
    color: 'info',
    change: '-2.5%',
  },
]

// Chart data and options for Shipment Statistics
const shipmentChartSeries = [
  {
    name: 'Shipment',
    data: [38, 45, 33, 38, 32, 50, 48, 40, 42, 37],
  },
  {
    name: 'Delivery',
    data: [23, 28, 20, 23, 18, 35, 33, 28, 30, 23],
  },
]

const shipmentChartOptions = computed(() => {
  const currentTheme = vuetifyTheme.current.value.colors
  const variableTheme = vuetifyTheme.current.value.variables

  return {
    chart: {
      parentHeightOffset: 0,
      toolbar: { show: false },
      type: 'bar',
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '30%',
        borderRadius: 4,
        startingShape: 'rounded',
        endingShape: 'rounded',
      },
    },
    colors: ['rgb(255,180,0)', 'rgb(144,85,253)'],
    dataLabels: {
      enabled: false,
    },
    stroke: {
      show: true,
      width: 2,
      colors: ['transparent'],
    },
    xaxis: {
      categories: ['1 Jan', '2 Jan', '3 Jan', '4 Jan', '5 Jan', '6 Jan', '7 Jan', '8 Jan', '9 Jan', '10 Jan'],
      labels: {
        style: {
          colors: `rgba(${hexToRgb(String(currentTheme['on-surface']))},${variableTheme['disabled-opacity']})`,
          fontSize: '13px',
          fontFamily: 'Inter',
        },
      },
      axisBorder: {
        show: false,
      },
      axisTicks: {
        show: false,
      },
    },
    yaxis: {
      labels: {
        formatter: (value: number) => `${value}%`,
        style: {
          colors: `rgba(${hexToRgb(String(currentTheme['on-surface']))},${variableTheme['disabled-opacity']})`,
          fontSize: '13px',
          fontFamily: 'Inter',
        },
      },
    },
    fill: {
      opacity: 1,
    },
    legend: {
      position: 'bottom',
      horizontalAlign: 'center',
      markers: {
        width: 8,
        height: 8,
        radius: 12,
      },
      itemMargin: {
        horizontal: 10,
      },
      labels: {
        colors: `rgba(${hexToRgb(String(currentTheme['on-surface']))},${variableTheme['high-emphasis-opacity']})`,
        useSeriesColors: false,
      },
    },
    grid: {
      borderColor: `rgba(${hexToRgb(String(variableTheme['border-color']))},${variableTheme['border-opacity']})`,
      strokeDashArray: 8,
      xaxis: {
        lines: {
          show: false,
        },
      },
      yaxis: {
        lines: {
          show: true,
        },
      },
      padding: {
        top: 0,
        right: 0,
        bottom: -5,
        left: 20,
      },
    },
    tooltip: {
      theme: 'light',
    },
  }
})

// Total Sales Donut Chart
const totalSalesDonutChartSeries = [45, 10, 18, 27]
const totalSalesDonutChartOptions = computed(() => {
  const currentTheme = vuetifyTheme.current.value.colors

  return {
    chart: {
      type: 'donut',
    },
    labels: ['Comments', 'Replies', 'Shares', 'Likes'],
    colors: [
      `rgb(${hexToRgb(String(currentTheme.primary))})`,
      `rgb(${hexToRgb(String(currentTheme.info))})`,
      `rgb(${hexToRgb(String(currentTheme.warning))})`,
      `rgb(${hexToRgb(String(currentTheme.error))})`,
    ],
    stroke: { width: 5, colors: ['#fff'] }, // Ensure stroke.colors is an array
    dataLabels: {
      enabled: true,
      formatter: (val: number, opts: any) => `${opts.w.globals.seriesNames[opts.seriesIndex]}`,
    },
    legend: { show: false },
    tooltip: {
      theme: 'dark', // Example from provided HTML
    },
    grid: {
      padding: {
        top: -12, // Example from provided HTML
        bottom: -12, // Example from provided HTML
      },
    },
    plotOptions: {
      pie: {
        donut: {
          size: '75%',
          labels: {
            show: true,
            value: {
              fontSize: '1.125rem',
              color: `rgba(${hexToRgb(String(currentTheme['on-surface']))},${vuetifyTheme.current.value.variables['high-emphasis-opacity']})`,
              fontWeight: 500,
              offsetY: -15,
              formatter: (val: number) => `${val}%`,
            },
            name: {
              offsetY: 20,
              fontFamily: 'Inter',
            },
            total: {
              show: true,
              label: '1 Quarter',
              fontSize: '0.8125rem',
              formatter: (w: any) => '28%',
              color: `rgba(${hexToRgb(String(currentTheme['on-surface']))},${vuetifyTheme.current.value.variables['medium-emphasis-opacity']})`,
            },
          },
        },
      },
    },
  }
})

// Total Revenue Line Chart
const totalRevenueLineChartSeries = [
  {
    name: 'series-1',
    data: [63, 18, 45, 3],
  },
]
const totalRevenueLineChartOptions = computed(() => {
  const currentTheme = vuetifyTheme.current.value.colors

  return {
    chart: {
      type: 'line',
      toolbar: { show: false },
      parentHeightOffset: 0,
      sparkline: { enabled: true },
    },
    grid: {
      show: false,
      padding: {
        top: -12, // Example from provided HTML
        bottom: -28, // Example from provided HTML for markers
        left: -28, // Example for markers
        right: -28, // Example for markers
      },
    },
    colors: [`rgb(${hexToRgb(String(currentTheme.primary))})`],
    stroke: {
      width: 5,
      curve: 'smooth',
    },
    markers: {
      size: 6,
      colors: ['transparent'],
      strokeColors: `rgb(${hexToRgb(String(currentTheme.primary))})`,
      strokeWidth: 4,
      discrete: [
        {
          seriesIndex: 0,
          dataPointIndex: 3, // Last point
          fillColor: '#fff',
          strokeColor: `rgb(${hexToRgb(String(currentTheme.primary))})`,
          size: 6,
        },
      ],
      hover: {
        size: 7,
      },
    },
    xaxis: {
      labels: { show: false },
      axisBorder: { show: false },
      axisTicks: { show: false },
    },
    yaxis: {
      labels: { show: false },
    },
    tooltip: { enabled: false },
    fill: { // Example from provided HTML filter
      type: 'solid',
      opacity: 0.09,
      // colors: [currentTheme.primary] // This was an example, might need adjustment
    },
    // filter: { // Example from provided HTML filter, might be complex to directly translate
    //   type: 'dropShadow',
    //   shadowBlur: 4,
    //   shadowColor: currentTheme.primary,
    //   shadowOffsetX: 2,
    //   shadowOffsetY: 10,
    //   shadowOpacity: 0.09,
    // }
  }
})

// Total Sales Radial Bar Chart
const totalSalesRadialChartSeries = [78]
const totalSalesRadialChartOptions = computed(() => {
  const currentTheme = vuetifyTheme.current.value.colors

  return {
    chart: {
      type: 'radialBar',
      sparkline: { enabled: true },
    },
    plotOptions: {
      radialBar: {
        startAngle: -90,
        endAngle: 90,
        hollow: {
          size: '47%', // Adjusted from example
        },
        track: {
          background: `rgba(${hexToRgb(String(currentTheme.secondary))}, 0.15)`, // Example, adjust as needed
          // background: 'rgba(240,242,248,0.85)' // from example
          margin: 10, // Example from placeholder
        },
        dataLabels: {
          show: true,
          name: {
            show: false,
          },
          value: {
            offsetY: 0, // Adjusted from -2 example in placeholder
            fontSize: '1.125rem',
            fontWeight: 500,
            color: `rgba(${hexToRgb(String(currentTheme['on-surface']))},${vuetifyTheme.current.value.variables['medium-emphasis-opacity']})`,
          },
        },
      },
    },
    colors: [`rgb(${hexToRgb(String(currentTheme.info))})`], // Example color from example
    // colors: ['rgba(22,177,255,0.85)'], // From example, using info theme color
    stroke: {
      lineCap: 'round',
    },
    grid: {
      padding: {
        top: -6, // Adjusted
        bottom: -6, // Adjusted
      },
    },
  }
})
</script>

<style lang="scss" scoped>
.logistics-card-statistics {
  border-block-end-style: solid;
  border-block-end-width: 2px;
}

.bubble {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 8px;
}
</style>