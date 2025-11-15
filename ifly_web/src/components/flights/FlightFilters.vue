<template>
    <div class="filters-panel">
        <div class="filters-header">
            <h3>筛选条件</h3>
            <el-button v-if="isMobile" icon="el-icon-close" size="mini" circle @click="closeFilters"></el-button>
        </div>

        <div class="filter-group">
            <h4>出发时间</h4>
            <el-slider v-model="localFilters.departureTimeRange" range :min="0" :max="24" :format-tooltip="formatHour"
                @change="applyFilters"></el-slider>
            <div class="time-range-display">
                <span>{{ formatHour(localFilters.departureTimeRange[0]) }}</span>
                <span>{{ formatHour(localFilters.departureTimeRange[1]) }}</span>
            </div>
        </div>

        <div class="filter-group">
            <h4>价格范围</h4>
            <el-slider v-model="localFilters.priceRange" range :min="minPrice" :max="maxPrice"
                :format-tooltip="val => `¥${val}`" @change="applyFilters"></el-slider>
            <div class="price-range-display">
                <span>¥{{ localFilters.priceRange[0] }}</span>
                <span>¥{{ localFilters.priceRange[1] }}</span>
            </div>
        </div>

        <div class="filter-group">
            <h4>航空公司</h4>
            <el-checkbox-group v-model="localFilters.airlines" @change="applyFilters">
                <el-checkbox v-for="airline in availableAirlines" :key="airline.code" :label="airline.code">
                    {{ airline.name }}
                </el-checkbox>
            </el-checkbox-group>
        </div>

        <div class="filter-group">
            <h4>其他选项</h4>
            <el-checkbox v-model="localFilters.directOnly" @change="applyFilters">只看直飞</el-checkbox>
            <el-checkbox v-model="localFilters.hasDiscount" @change="applyFilters">只看特价</el-checkbox>
        </div>

        <el-button type="info" plain @click="resetFilters" class="reset-btn">重置所有筛选</el-button>
    </div>
</template>

<script>
export default {
    name: 'FlightFilters',
    props: {
        filters: {
            type: Object,
            required: true
        },
        availableAirlines: {
            type: Array,
            required: true
        },
        minPrice: {
            type: Number,
            required: true
        },
        maxPrice: {
            type: Number,
            required: true
        },
        isMobile: {
            type: Boolean,
            default: false
        }
    },
    data() {
        return {
            localFilters: JSON.parse(JSON.stringify(this.filters))
        };
    },
    watch: {
        filters: {
            handler(newVal) {
                this.localFilters = JSON.parse(JSON.stringify(newVal));
            },
            deep: true
        }
    },
    methods: {
        formatHour(hour) {
            return `${hour}:00`;
        },
        applyFilters() {
            this.$emit('filter-changed', this.localFilters);
        },
        resetFilters() {
            this.$emit('reset-filters');
        },
        closeFilters() {
            this.$emit('close-filters');
        }
    }
}
</script>

<style scoped>
.filters-panel {
    background: #fff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    margin-right: 20px;
    width: 280px;
    flex-shrink: 0;
}

.filters-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.filter-group {
    margin-bottom: 24px;
}

.filter-group h4 {
    margin-bottom: 12px;
    font-size: 16px;
    font-weight: 500;
    color: #303133;
}

.time-range-display,
.price-range-display {
    display: flex;
    justify-content: space-between;
    margin-top: 5px;
    font-size: 13px;
    color: #606266;
}

.reset-btn {
    width: 100%;
    margin-top: 10px;
}

@media (max-width: 768px) {
    .filters-panel {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 2000;
        width: 100%;
        margin: 0;
        overflow-y: auto;
    }
}
</style>