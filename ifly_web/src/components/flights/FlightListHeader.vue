<template>
    <div class="list-header">
        <div class="mobile-filter-toggle" v-if="isMobile">
            <el-button type="primary" plain size="small" @click="showFilters" icon="el-icon-s-operation">
                筛选
            </el-button>
        </div>
        <div class="found-count">找到 <span class="count-highlight">{{ flightCount }}</span> 个航班</div>
        <div class="sort-options">
            <span>排序方式:</span>
            <el-radio-group v-model="currentSort" size="small" @change="handleSortChange">
                <el-radio-button label="recommended">推荐</el-radio-button>
                <el-radio-button label="price">价格</el-radio-button>
                <el-radio-button label="departureTime">起飞时间</el-radio-button>
                <el-radio-button label="duration">飞行时间</el-radio-button>
            </el-radio-group>
        </div>
    </div>
</template>

<script>
export default {
    name: 'FlightListHeader',
    props: {
        flightCount: {
            type: Number,
            required: true
        },
        sortOption: {
            type: String,
            default: 'recommended'
        },
        isMobile: {
            type: Boolean,
            default: false
        }
    },
    data() {
        return {
            currentSort: this.sortOption
        };
    },
    watch: {
        sortOption(newVal) {
            this.currentSort = newVal;
        }
    },
    methods: {
        handleSortChange(value) {
            this.$emit('sort-changed', value);
        },
        showFilters() {
            this.$emit('show-filters');
        }
    }
}
</script>

<style scoped>
.list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.found-count {
    font-size: 16px;
    color: #606266;
}

.count-highlight {
    font-weight: bold;
    color: #409EFF;
}

.sort-options {
    display: flex;
    align-items: center;
}

.sort-options span {
    margin-right: 10px;
    color: #606266;
}

@media (max-width: 768px) {
    .list-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }

    .sort-options {
        width: 100%;
        overflow-x: auto;
        padding-bottom: 5px;
    }
}
</style>