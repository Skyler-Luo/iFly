from django.urls import path
from .views import (
    AnalyticsOverview,
    FlightAnalytics,
    RevenueAnalytics,
    BusinessIntelligence,
    DataVisualization,
    SystemLog,
    SalesTrend,
    UserAnalytics,
    FlightVisualization,
    SalesPrediction,
    RouteAnalytics,
    PriceElasticity,
    CustomerLTV,
    SeasonalityAnalysis,
    AnomalyDetection,
    SalesAnalytics,
    CustomerSegments,
    RouteMap,
    CustomerLoyalty,
    PivotData,
    RealtimeData
)

urlpatterns = [
    path('overview/', AnalyticsOverview.as_view(), name='analytics-overview'),
    path('flights/', FlightAnalytics.as_view(), name='flight-analytics'),
    path('revenue/', RevenueAnalytics.as_view(), name='revenue-analytics'),
    path('business-intelligence/', BusinessIntelligence.as_view(), name='business-intelligence'),
    path('visualization/', DataVisualization.as_view(), name='data-visualization'),
    path('logs/', SystemLog.as_view(), name='system-logs'),
    path('admin/dashboard/stats/', AnalyticsOverview.as_view(), name='admin-dashboard-stats'),
    
    # 数据可视化相关
    path('visualization/sales-trend/', SalesTrend.as_view(), name='visualization-sales-trend'),
    path('visualization/user-analytics/', UserAnalytics.as_view(), name='visualization-user-analytics'),
    path('visualization/flight-analytics/', FlightVisualization.as_view(), name='visualization-flight-analytics'),
    
    # 商业智能相关
    path('business-intelligence/sales-prediction/', SalesPrediction.as_view(), name='bi-sales-prediction'),
    path('business-intelligence/route-analytics/', RouteAnalytics.as_view(), name='bi-route-analytics'),
    path('business-intelligence/price-elasticity/', PriceElasticity.as_view(), name='bi-price-elasticity'),
    path('business-intelligence/customer-ltv/', CustomerLTV.as_view(), name='bi-customer-ltv'),
    path('business-intelligence/seasonality/', SeasonalityAnalysis.as_view(), name='bi-seasonality'),
    path('business-intelligence/anomalies/', AnomalyDetection.as_view(), name='bi-anomalies'),
    
    # 综合分析相关
    path('sales/', SalesAnalytics.as_view(), name='sales-analytics'),
    path('customers/segments/', CustomerSegments.as_view(), name='customer-segments'),
    path('routes/map/', RouteMap.as_view(), name='route-map'),
    path('customers/loyalty/', CustomerLoyalty.as_view(), name='customer-loyalty'),
    path('pivot-data/', PivotData.as_view(), name='pivot-data'),
    path('realtime/', RealtimeData.as_view(), name='realtime-data'),
] 