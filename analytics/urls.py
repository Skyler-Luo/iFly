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
    RouteAnalytics,
    SalesAnalytics,
    CustomerSegments,
    CustomerLoyalty,
    RouteMap,
    PivotData,
    RealtimeData,
    # 多维度分析模块 API - Requirements 3, 4, 5
    MultiDimensionAnalysisView,
    PivotDataView,
    PivotExportView,
    TrendsView,
    # 航线推荐 API - Requirement 4
    RouteRecommendationView,
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
    path('business-intelligence/route-analytics/', RouteAnalytics.as_view(), name='bi-route-analytics'),
    # 多维度分析 API - 满足 Requirement 3
    path('business-intelligence/multi-dimension/', MultiDimensionAnalysisView.as_view(), name='bi-multi-dimension'),
    # 趋势分析 API - 满足 Requirement 5
    path('business-intelligence/trends/', TrendsView.as_view(), name='bi-trends'),
    
    # 综合分析相关
    path('sales/', SalesAnalytics.as_view(), name='sales-analytics'),
    path('customers/segments/', CustomerSegments.as_view(), name='customer-segments'),
    path('customers/loyalty/', CustomerLoyalty.as_view(), name='customer-loyalty'),
    path('routes/map/', RouteMap.as_view(), name='route-map'),
    path('pivot-data/', PivotData.as_view(), name='pivot-data'),
    # 透视表 API - 满足 Requirement 4
    path('pivot-table/', PivotDataView.as_view(), name='pivot-table'),
    path('pivot-table/export/', PivotExportView.as_view(), name='pivot-table-export'),
    path('realtime/', RealtimeData.as_view(), name='realtime-data'),
    
    # 航线推荐 API - 满足 Requirement 4
    path('recommendations/routes/', RouteRecommendationView.as_view(), name='route-recommendations'),
]