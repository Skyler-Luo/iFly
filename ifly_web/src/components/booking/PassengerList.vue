<template>
    <div class="passengers-container">
        <div class="section-title">
            <h2>乘客信息</h2>
            <div class="passenger-count">
                共 {{ passengers.length }} 位乘客
            </div>
        </div>

        <el-collapse v-model="activePassengers">
            <el-collapse-item v-for="(passenger, index) in passengers" :key="index"
                :title="`乘客 ${index + 1}${passenger.isComplete ? ' (已完成)' : ''}`" :name="index">
                <passenger-form :passenger="passenger" :has-saved-passengers="hasSavedPassengers" :index="index"
                    @save="handlePassengerSave" @use-existing="handleUseExisting" ref="passengerForms" />
            </el-collapse-item>
        </el-collapse>
    </div>
</template>

<script>
import PassengerForm from '@/components/PassengerForm.vue'

export default {
    name: 'PassengerList',
    components: {
        PassengerForm
    },
    props: {
        passengers: {
            type: Array,
            required: true
        },
        hasSavedPassengers: {
            type: Boolean,
            default: false
        }
    },
    data() {
        return {
            activePassengers: [0] // 默认展开第一个乘客
        };
    },
    methods: {
        handlePassengerSave(passenger, index) {
            this.$emit('passenger-save', passenger, index);

            // 如果还有下一位乘客，则展开下一位
            if (index < this.passengers.length - 1) {
                this.activePassengers = [index + 1];
            }
        },
        handleUseExisting(index) {
            this.$emit('use-existing', index);
        },
        validateAllPassengers() {
            if (!this.$refs.passengerForms) return Promise.resolve(false);

            const validations = this.$refs.passengerForms.map(form => {
                return form.validate();
            });

            return Promise.all(validations).then(results => {
                return results.every(result => result === true);
            });
        },
        expandPassenger(index) {
            this.activePassengers = [index];
        }
    }
}
</script>

<style scoped>
.passengers-container {
    margin-bottom: 30px;
}

.section-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.section-title h2 {
    margin: 0;
    font-size: 20px;
    font-weight: 500;
}

.passenger-count {
    background-color: #f0f9eb;
    color: #67c23a;
    padding: 5px 10px;
    border-radius: 4px;
    font-size: 14px;
}

@media (max-width: 768px) {
    .section-title {
        flex-direction: column;
        align-items: flex-start;
    }

    .passenger-count {
        margin-top: 10px;
    }
}
</style>