<template>
    <div class="seat-selection-container">
        <div class="seat-map-legend">
            <div class="legend-item">
                <div class="seat-icon available"></div>
                <span>可选座位</span>
            </div>
            <div class="legend-item">
                <div class="seat-icon selected"></div>
                <span>已选座位</span>
            </div>
            <div class="legend-item">
                <div class="seat-icon occupied"></div>
                <span>已售座位</span>
            </div>
        </div>

        <div class="aircraft-cabin">
            <div class="cabin-header">
                <div class="cabin-exit left">出口</div>
                <div class="cabin-name">{{ cabinLabel }}</div>
                <div class="cabin-exit right">出口</div>
            </div>

            <div class="seat-map">
                <div class="aisle-label">
                    <span v-for="col in columns" :key="col">{{ col }}</span>
                </div>

                <div v-for="row in rows" :key="row" class="seat-row">
                    <div class="row-label">{{ row }}</div>

                    <template v-for="(col, colIndex) in columns" :key="`seat-group-${row}-${colIndex}`">
                        <div v-if="isAisle(colIndex)" class="aisle"></div>

                        <div class="seat" :class="getSeatClass(row, col)" @click="selectSeat(row, col)">
                            <span v-if="!isSeatOccupied(row, col)">{{ row }}{{ col }}</span>
                            <span v-else>X</span>
                        </div>
                    </template>

                    <div class="row-label">{{ row }}</div>
                </div>
            </div>
        </div>

        <div class="selected-seats-info">
            <h3>已选座位</h3>
            <div class="selected-seats-list">
                <div v-if="selectedSeats.length === 0" class="no-seats-selected">
                    请为每位乘客选择座位
                </div>
                <div v-for="(seat, index) in selectedSeats" :key="index" class="selected-seat-item">
                    <span class="seat-label">{{ seat.row }}{{ seat.column }}</span>
                    <span class="passenger-name">
                        {{ passengerNames[index] || `乘客 ${index + 1}` }}
                    </span>
                    <el-button type="danger" size="mini" icon="el-icon-delete" circle @click="removeSeat(index)">
                    </el-button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'SeatMap',
    props: {
        cabinLabel: {
            type: String,
            default: '经济舱'
        },
        maxSeats: {
            type: Number,
            default: 1
        },
        passengerNames: {
            type: Array,
            default: () => []
        },
        occupiedSeats: {
            type: Array,
            default: () => []
        }
    },
    data() {
        return {
            rows: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
            columns: ['1', '2', '3', '4', '5', '6', '7', '8', '9'],
            selectedSeats: []
        };
    },
    methods: {
        isAisle(colIndex) {
            // 通道位置设置 (在第3和第6列之间)
            return colIndex === 2 || colIndex === 5;
        },
        isSeatOccupied(row, col) {
            return this.occupiedSeats.some(seat => seat.row === row && seat.column === col);
        },
        isSeatSelected(row, col) {
            return this.selectedSeats.some(seat => seat.row === row && seat.column === col);
        },
        getSeatClass(row, col) {
            if (this.isSeatOccupied(row, col)) {
                return 'occupied';
            } else if (this.isSeatSelected(row, col)) {
                return 'selected';
            } else {
                return 'available';
            }
        },
        selectSeat(row, col) {
            // 如果座位已经被占用，则不能选择
            if (this.isSeatOccupied(row, col)) {
                return;
            }

            // 如果座位已经被选择，则取消选择
            const selectedIndex = this.selectedSeats.findIndex(seat => seat.row === row && seat.column === col);
            if (selectedIndex > -1) {
                this.selectedSeats.splice(selectedIndex, 1);
                this.$emit('update:seats', [...this.selectedSeats]);
                return;
            }

            // 如果已经选择了最大数量的座位，则不能再选择
            if (this.selectedSeats.length >= this.maxSeats) {
                this.$message.warning(`最多只能选择${this.maxSeats}个座位`);
                return;
            }

            // 添加新选择的座位
            this.selectedSeats.push({ row, column: col });
            this.$emit('update:seats', [...this.selectedSeats]);
        },
        removeSeat(index) {
            this.selectedSeats.splice(index, 1);
            this.$emit('update:seats', [...this.selectedSeats]);
        },
        getSelectedSeats() {
            return this.selectedSeats;
        }
    }
};
</script>

<style scoped>
.seat-selection-container {
    margin: 20px 0;
}

.seat-map-legend {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
}

.legend-item {
    display: flex;
    align-items: center;
    margin: 0 15px;
}

.seat-icon {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    margin-right: 8px;
    border: 1px solid #ddd;
}

.seat-icon.available {
    background-color: #ffffff;
}

.seat-icon.selected {
    background-color: #42A5F5;
}

.seat-icon.occupied {
    background-color: #e0e0e0;
    position: relative;
}

.seat-icon.occupied:after {
    content: "X";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #757575;
    font-size: 12px;
}

.aircraft-cabin {
    background: #f5f5f5;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
}

.cabin-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.cabin-name {
    font-size: 18px;
    font-weight: bold;
}

.cabin-exit {
    background: #ff5252;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
}

.seat-map {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.aisle-label {
    display: flex;
    padding: 0 40px;
    margin-bottom: 10px;
}

.aisle-label span {
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 2px;
    font-weight: bold;
}

.seat-row {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
}

.row-label {
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
}

.seat {
    width: 30px;
    height: 30px;
    margin: 0 2px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 10px;
}

.seat.available {
    background-color: white;
}

.seat.available:hover {
    background-color: #e3f2fd;
    transform: translateY(-2px);
}

.seat.selected {
    background-color: #42A5F5;
    color: white;
    border-color: #1976d2;
}

.seat.occupied {
    background-color: #e0e0e0;
    cursor: not-allowed;
    color: #757575;
}

.aisle {
    width: 20px;
}

.selected-seats-info {
    margin-top: 30px;
    background: #f5f5f5;
    padding: 20px;
    border-radius: 8px;
}

.selected-seats-list {
    margin-top: 10px;
}

.no-seats-selected {
    color: #757575;
    font-style: italic;
}

.selected-seat-item {
    display: flex;
    align-items: center;
    padding: 10px;
    border-bottom: 1px solid #e0e0e0;
}

.selected-seat-item:last-child {
    border-bottom: none;
}

.seat-label {
    background: #42A5F5;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    margin-right: 15px;
}

.passenger-name {
    flex: 1;
}
</style>