<template>
    <div class="admin-users">
        <h1 class="title">用户管理</h1>

        <div class="top-actions">
            <div class="search-bar">
                <input type="text" v-model="searchQuery" placeholder="搜索用户名、邮箱、手机号..." />
                <button @click="handleSearch" class="btn-search">
                    <i class="fas fa-search"></i>
                </button>
            </div>

            <div class="filter-options">
                <select v-model="roleFilter">
                    <option value="">所有角色</option>
                    <option value="user">普通用户</option>
                    <option value="vip">VIP用户</option>
                    <option value="admin">管理员</option>
                </select>

                <select v-model="statusFilter">
                    <option value="">所有状态</option>
                    <option value="active">活跃</option>
                    <option value="inactive">未激活</option>
                    <option value="locked">已锁定</option>
                </select>
            </div>

            <button @click="showAddUserModal = true" class="btn btn-primary">
                <i class="fas fa-user-plus"></i> 添加用户
            </button>
        </div>

        <div v-if="isLoading" class="loading-container">
            <div class="spinner"></div>
            <p>正在加载数据...</p>
        </div>

        <div v-else-if="error" class="error-container">
            <i class="fas fa-exclamation-triangle"></i>
            <p>{{ error }}</p>
            <button @click="fetchUsers" class="btn btn-primary">重新加载</button>
        </div>

        <div v-else class="data-table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th @click="sortBy('id')">
                            ID
                            <i class="fas" :class="getSortIconClass('id')"></i>
                        </th>
                        <th @click="sortBy('username')">
                            用户名
                            <i class="fas" :class="getSortIconClass('username')"></i>
                        </th>
                        <th @click="sortBy('email')">
                            邮箱
                            <i class="fas" :class="getSortIconClass('email')"></i>
                        </th>
                        <th @click="sortBy('phone')">
                            手机号
                            <i class="fas" :class="getSortIconClass('phone')"></i>
                        </th>
                        <th @click="sortBy('role')">
                            角色
                            <i class="fas" :class="getSortIconClass('role')"></i>
                        </th>
                        <th @click="sortBy('points')">
                            积分
                            <i class="fas" :class="getSortIconClass('points')"></i>
                        </th>
                        <th @click="sortBy('status')">
                            状态
                            <i class="fas" :class="getSortIconClass('status')"></i>
                        </th>
                        <th @click="sortBy('registerDate')">
                            注册时间
                            <i class="fas" :class="getSortIconClass('registerDate')"></i>
                        </th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="user in filteredUsers" :key="user.id">
                        <td>{{ user.id }}</td>
                        <td>{{ user.username }}</td>
                        <td>{{ user.email }}</td>
                        <td>{{ user.phone }}</td>
                        <td>
                            <span class="role-badge" :class="'role-' + user.role">
                                {{ getRoleText(user.role) }}
                            </span>
                        </td>
                        <td>{{ user.points }}</td>
                        <td>
                            <span class="status-badge" :class="'status-' + user.status">
                                {{ getStatusText(user.status) }}
                            </span>
                        </td>
                        <td>{{ formatDate(user.registerDate) }}</td>
                        <td class="actions-cell">
                            <button @click="editUser(user)" class="btn-icon">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button @click="openDeleteConfirm(user)" class="btn-icon">
                                <i class="fas fa-trash-alt"></i>
                            </button>
                            <div class="dropdown">
                                <button class="btn-icon dropdown-toggle">
                                    <i class="fas fa-ellipsis-v"></i>
                                </button>
                                <div class="dropdown-menu">
                                    <a @click="viewUserOrders(user.id)">查看订单</a>
                                    <a @click="updateUserStatus(user.id, 'active')"
                                        v-if="user.status !== 'active'">激活账户</a>
                                    <a @click="updateUserStatus(user.id, 'locked')"
                                        v-if="user.status !== 'locked'">锁定账户</a>
                                    <a @click="resetUserPassword(user.id)">重置密码</a>
                                    <a @click="adjustUserPoints(user)">调整积分</a>
                                    <a @click="sendNotification(user.id)">发送通知</a>
                                </div>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>

            <div class="pagination">
                <button @click="prevPage" :disabled="currentPage === 1" class="btn-page">
                    <i class="fas fa-chevron-left"></i>
                </button>
                <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
                <button @click="nextPage" :disabled="currentPage === totalPages" class="btn-page">
                    <i class="fas fa-chevron-right"></i>
                </button>
            </div>
        </div>

        <!-- 添加/编辑用户弹窗 -->
        <div v-if="showAddUserModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>{{ isEditing ? '编辑用户' : '添加用户' }}</h2>
                    <button @click="closeModal" class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="submitUserForm">
                        <div class="form-row">
                            <div class="form-group">
                                <label>用户名</label>
                                <input type="text" v-model="userForm.username" required />
                            </div>

                            <div class="form-group">
                                <label>密码{{ isEditing ? '（留空保持不变）' : '' }}</label>
                                <input type="password" v-model="userForm.password" :required="!isEditing" />
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label>邮箱</label>
                                <input type="email" v-model="userForm.email" required />
                            </div>

                            <div class="form-group">
                                <label>手机号</label>
                                <input type="tel" v-model="userForm.phone" required />
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label>角色</label>
                                <select v-model="userForm.role" required>
                                    <option value="user">普通用户</option>
                                    <option value="vip">VIP用户</option>
                                    <option value="admin">管理员</option>
                                </select>
                            </div>

                            <div class="form-group">
                                <label>状态</label>
                                <select v-model="userForm.status" required>
                                    <option value="active">活跃</option>
                                    <option value="inactive">未激活</option>
                                    <option value="locked">已锁定</option>
                                </select>
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label>积分</label>
                                <input type="number" v-model="userForm.points" min="0" />
                            </div>

                            <div class="form-group">
                                <label>真实姓名</label>
                                <input type="text" v-model="userForm.realName" />
                            </div>
                        </div>

                        <div class="form-group">
                            <label>地址</label>
                            <textarea v-model="userForm.address" rows="2"></textarea>
                        </div>

                        <div class="form-actions">
                            <button type="button" @click="closeModal" class="btn btn-secondary">取消</button>
                            <button type="submit" class="btn btn-primary">{{ isEditing ? '保存修改' : '添加用户' }}</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <!-- 确认删除弹窗 -->
        <div v-if="showDeleteConfirm" class="modal">
            <div class="modal-content modal-sm">
                <div class="modal-header">
                    <h2>确认删除</h2>
                    <button @click="showDeleteConfirm = false" class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <p>确定要删除用户 {{ selectedUser?.username }} 吗？此操作不可撤销。</p>
                    <div class="form-actions">
                        <button @click="showDeleteConfirm = false" class="btn btn-secondary">取消</button>
                        <button @click="deleteUser" class="btn btn-danger">确认删除</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 调整积分弹窗 -->
        <div v-if="showPointsModal" class="modal">
            <div class="modal-content modal-sm">
                <div class="modal-header">
                    <h2>调整积分</h2>
                    <button @click="showPointsModal = false" class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <p>用户: {{ selectedUser?.username }}</p>
                    <p>当前积分: {{ selectedUser?.points }}</p>

                    <div class="form-group">
                        <label>积分变更</label>
                        <div class="points-adjust">
                            <select v-model="pointsAdjustType">
                                <option value="add">增加</option>
                                <option value="subtract">减少</option>
                                <option value="set">设置为</option>
                            </select>
                            <input type="number" v-model="pointsAdjustValue" min="0" required />
                        </div>
                    </div>

                    <div class="form-group">
                        <label>变更原因</label>
                        <textarea v-model="pointsAdjustReason" rows="2" placeholder="请输入积分变更原因"></textarea>
                    </div>

                    <div class="form-actions">
                        <button @click="showPointsModal = false" class="btn btn-secondary">取消</button>
                        <button @click="submitPointsAdjust" class="btn btn-primary">确认</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 发送通知弹窗 -->
        <div v-if="showNotificationModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>发送通知</h2>
                    <button @click="showNotificationModal = false" class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <p>接收用户: {{ selectedUser?.username }}</p>

                    <div class="form-group">
                        <label>通知标题</label>
                        <input type="text" v-model="notificationForm.title" required />
                    </div>

                    <div class="form-group">
                        <label>通知内容</label>
                        <textarea v-model="notificationForm.content" rows="4" required></textarea>
                    </div>

                    <div class="form-group">
                        <label>通知类型</label>
                        <select v-model="notificationForm.type">
                            <option value="system">系统通知</option>
                            <option value="promotion">促销通知</option>
                            <option value="account">账户通知</option>
                            <option value="order">订单通知</option>
                        </select>
                    </div>

                    <div class="form-actions">
                        <button @click="showNotificationModal = false" class="btn btn-secondary">取消</button>
                        <button @click="submitNotification" class="btn btn-primary">发送</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import api from '../services/api';

export default {
    name: 'AdminUsersView',
    data() {
        return {
            users: [],
            isLoading: false,
            error: null,
            searchQuery: '',
            roleFilter: '',
            statusFilter: '',
            sortKey: '',
            sortDirection: 'asc',
            currentPage: 1,
            pageSize: 5,
            showAddUserModal: false,
            showDeleteConfirm: false,
            showPointsModal: false,
            selectedUser: null,
            isEditing: false,
            userForm: {
                username: '',
                password: '',
                email: '',
                phone: '',
                role: 'user',
                status: 'active',
                points: 0,
                realName: '',
                address: '',
            },
            pointsAdjustType: 'add',
            pointsAdjustValue: 0,
            pointsAdjustReason: '',
        }
    },
    computed: {
        filteredUsers() {
            let filtered = this.users;
            if (this.searchQuery) {
                const query = this.searchQuery.toLowerCase();
                filtered = filtered.filter(user =>
                    user.username.toLowerCase().includes(query) ||
                    user.email.toLowerCase().includes(query) ||
                    user.phone.includes(query)
                );
            }
            if (this.roleFilter) {
                filtered = filtered.filter(user => user.role === this.roleFilter);
            }
            if (this.statusFilter) {
                filtered = filtered.filter(user => user.status === this.statusFilter);
            }
            if (this.sortKey) {
                filtered = filtered.sort((a, b) => {
                    const aValue = a[this.sortKey];
                    const bValue = b[this.sortKey];
                    if (this.sortDirection === 'asc') {
                        return aValue < bValue ? -1 : 1;
                    } else {
                        return aValue > bValue ? -1 : 1;
                    }
                });
            }
            const start = (this.currentPage - 1) * this.pageSize;
            const end = start + this.pageSize;
            return filtered.slice(start, end);
        },
        totalPages() {
            return Math.ceil(this.filteredUsers.length / this.pageSize);
        }
    },
    methods: {
        // 获取用户数据
        async fetchUsers() {
            this.isLoading = true;
            this.error = null;

            try {
                const params = {};
                if (this.searchQuery) params.search = this.searchQuery;
                if (this.roleFilter) params.role = this.roleFilter;
                if (this.statusFilter) params.status = this.statusFilter;

                const response = await api.admin.users.getList(params);
                if (Array.isArray(response.data)) {
                    this.users = response.data;
                } else {
                    console.warn('API返回的用户数据不是数组，使用空数组');
                    this.users = [];
                }

                console.log('获取到用户数据:', this.users);

                // 如果返回的数据为空，使用模拟数据
                if (!this.users || this.users.length === 0) {
                    console.warn('API返回的用户数据为空，使用默认数据');
                    this.useDefaultData();
                }
            } catch (error) {
                console.error('获取用户数据失败:', error);
                this.error = '获取用户数据失败，请稍后再试';

                // 确保users是数组
                this.users = [];
                // API调用失败，使用模拟数据
                this.useDefaultData();
            } finally {
                this.isLoading = false;
            }
        },

        // 添加用户
        async addUser() {
            try {
                const response = await api.admin.users.create(this.userForm);
                this.users.push(response.data);
                this.closeModal();
                this.fetchUsers(); // 重新获取所有用户数据
            } catch (error) {
                console.error('添加用户失败:', error);
                alert('添加用户失败，请稍后再试');
            }
        },

        // 更新用户
        async updateUser() {
            try {
                await api.admin.users.update(this.selectedUser.id, this.userForm);
                this.closeModal();
                this.fetchUsers(); // 重新获取所有用户数据
            } catch (error) {
                console.error('更新用户失败:', error);
                alert('更新用户失败，请稍后再试');
            }
        },

        // 删除用户
        async deleteUser() {
            try {
                await api.admin.users.delete(this.selectedUser.id);
                this.users = this.users.filter(user => user.id !== this.selectedUser.id);
                this.showDeleteConfirm = false;
            } catch (error) {
                console.error('删除用户失败:', error);
                alert('删除用户失败，请稍后再试');
            }
        },

        // 更新用户状态
        async updateUserStatus(userId, status) {
            try {
                await api.admin.users.updateStatus(userId, status);
                const index = this.users.findIndex(user => user.id === userId);
                if (index !== -1) {
                    this.users[index].status = status;
                }
            } catch (error) {
                console.error('更新用户状态失败:', error);
                alert('更新用户状态失败，请稍后再试');
            }
        },

        // 重置用户密码
        async resetUserPassword(userId) {
            try {
                await api.admin.users.resetPassword(userId);
                alert('密码重置邮件已发送');
            } catch (error) {
                console.error('重置密码失败:', error);
                alert('重置密码失败，请稍后再试');
            }
        },

        // 查看用户订单
        async viewUserOrders(userId) {
            try {
                const response = await api.admin.users.getUserOrders(userId);
                console.log('用户订单数据:', response.data);
                // 这里可以添加显示订单数据的逻辑，或者跳转到订单详情页面
                this.$router.push(`/admin/users/${userId}/orders`);
            } catch (error) {
                console.error('获取用户订单失败:', error);
                alert('获取用户订单失败，请稍后再试');
            }
        },

        // 调整用户积分
        async adjustUserPointsSubmit() {
            if (!this.selectedUser) return;

            let pointsChange = parseInt(this.pointsAdjustValue);
            if (isNaN(pointsChange) || pointsChange < 0) {
                alert('请输入有效的积分值');
                return;
            }

            const data = {
                type: this.pointsAdjustType,
                points: pointsChange,
                reason: this.pointsAdjustReason
            };

            try {
                await api.admin.users.adjustPoints(this.selectedUser.id, data);

                // 更新本地用户数据
                const index = this.users.findIndex(user => user.id === this.selectedUser.id);
                if (index !== -1) {
                    if (this.pointsAdjustType === 'add') {
                        this.users[index].points += pointsChange;
                    } else if (this.pointsAdjustType === 'subtract') {
                        this.users[index].points = Math.max(0, this.users[index].points - pointsChange);
                    } else if (this.pointsAdjustType === 'set') {
                        this.users[index].points = pointsChange;
                    }
                }

                this.showPointsModal = false;
            } catch (error) {
                console.error('调整积分失败:', error);
                alert('调整积分失败，请稍后再试');
            }
        },

        // 发送通知
        async sendNotification(userId) {
            // 这里可以添加发送通知的弹窗和API调用
            const message = prompt('请输入要发送的通知内容:');
            if (!message) return;

            try {
                await api.admin.users.sendNotification(userId, { message });
                alert('通知已发送');
            } catch (error) {
                console.error('发送通知失败:', error);
                alert('发送通知失败，请稍后再试');
            }
        },

        // 表单提交
        submitUserForm() {
            if (this.isEditing) {
                this.updateUser();
            } else {
                this.addUser();
            }
        },

        handleSearch() {
            this.currentPage = 1;
            this.fetchUsers();
        },

        // 调整用户积分按钮点击
        adjustUserPoints(user) {
            this.selectedUser = user;
            this.pointsAdjustValue = 0;
            this.pointsAdjustType = 'add';
            this.pointsAdjustReason = '';
            this.showPointsModal = true;
        },

        // 关闭模态窗口
        closeModal() {
            this.showAddUserModal = false;
            this.isEditing = false;
            this.userForm = {
                username: '',
                password: '',
                email: '',
                phone: '',
                role: 'user',
                status: 'active',
                points: 0,
                realName: '',
                address: '',
            };
        },

        // 编辑用户
        editUser(user) {
            this.isEditing = true;
            this.selectedUser = user;
            this.userForm = { ...user, password: '' }; // 不填充密码
            this.showAddUserModal = true;
        },

        // 打开删除确认
        openDeleteConfirm(user) {
            this.selectedUser = user;
            this.showDeleteConfirm = true;
        },

        // 格式化日期
        formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleDateString('zh-CN');
        },

        // 角色文本
        getRoleText(role) {
            const roles = {
                'user': '普通用户',
                'vip': 'VIP用户',
                'admin': '管理员'
            };
            return roles[role] || role;
        },

        // 状态文本
        getStatusText(status) {
            const statuses = {
                'active': '活跃',
                'inactive': '未激活',
                'locked': '已锁定'
            };
            return statuses[status] || status;
        },

        // 排序图标
        getSortIconClass(key) {
            if (this.sortKey !== key) return 'fa-sort';
            return this.sortDirection === 'asc' ? 'fa-sort-up' : 'fa-sort-down';
        },

        // 排序
        sortBy(key) {
            if (this.sortKey === key) {
                this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                this.sortKey = key;
                this.sortDirection = 'asc';
            }
        },

        // 上一页
        prevPage() {
            if (this.currentPage > 1) {
                this.currentPage--;
            }
        },

        // 下一页
        nextPage() {
            if (this.currentPage < this.totalPages) {
                this.currentPage++;
            }
        },

        // 如果API调用失败，使用默认数据
        useDefaultData() {
            this.users = [
                {
                    id: 1,
                    username: 'zhangwei',
                    email: 'zhangwei@example.com',
                    phone: '13800138001',
                    role: 'user',
                    points: 2560,
                    status: 'active',
                    registerDate: '2022-12-15',
                    realName: '张伟',
                    address: '北京市海淀区中关村大街1号'
                },
                {
                    id: 2,
                    username: 'liming',
                    email: 'liming@example.com',
                    phone: '13900139002',
                    role: 'vip',
                    points: 5800,
                    status: 'active',
                    registerDate: '2023-01-20',
                    realName: '李明',
                    address: '上海市浦东新区陆家嘴金融中心'
                },
                {
                    id: 3,
                    username: 'wangjing',
                    email: 'wangjing@example.com',
                    phone: '13700137003',
                    role: 'user',
                    points: 1200,
                    status: 'inactive',
                    registerDate: '2023-03-05',
                    realName: '王静',
                    address: '广州市天河区珠江新城'
                }
            ];
        },
    },
    mounted() {
        this.fetchUsers();
    }
}
</script>

<style scoped>
/* ... existing styles ... */
.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    min-height: 200px;
}

.spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border-left-color: #3498db;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

.error-container {
    text-align: center;
    padding: 2rem;
    color: #e74c3c;
}

.error-container i {
    font-size: 2rem;
    margin-bottom: 1rem;
}
</style>