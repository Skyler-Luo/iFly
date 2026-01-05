<template>
    <div class="admin-users">
        <h1 class="title">用户管理</h1>

        <div class="top-actions">
            <el-input
                v-model="searchQuery"
                placeholder="搜索用户名、邮箱、手机号..."
                clearable
                style="width: 300px"
                @keyup.enter="handleSearch"
            >
                <template #prefix>
                    <i class="fas fa-search"></i>
                </template>
            </el-input>

            <el-radio-group v-model="roleFilter" @change="handleSearch">
                <el-radio-button value="">全部</el-radio-button>
                <el-radio-button value="user">普通用户</el-radio-button>
                <el-radio-button value="admin">管理员</el-radio-button>
            </el-radio-group>

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
                        <th @click="sortBy('registerDate')">
                            注册时间
                            <i class="fas" :class="getSortIconClass('registerDate')"></i>
                        </th>
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
                        <td>{{ formatDate(user.registerDate) }}</td>
                    </tr>
                </tbody>
            </table>

            <div class="pagination">
                <el-pagination
                    v-model:current-page="currentPage"
                    :page-size="pageSize"
                    :total="processedUsers.length"
                    layout="total, prev, pager, next"
                    background
                />
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
                                    <option value="admin">管理员</option>
                                </select>
                            </div>
                        </div>

                        <div class="form-group">
                            <label>真实姓名</label>
                            <input type="text" v-model="userForm.realName" />
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
            sortKey: '',
            sortDirection: 'asc',
            currentPage: 1,
            pageSize: 8,
            showAddUserModal: false,
            showDeleteConfirm: false,
            showNotificationModal: false,
            selectedUser: null,
            isEditing: false,
            userForm: {
                username: '',
                password: '',
                email: '',
                phone: '',
                role: 'user',
                realName: '',
                address: '',
            },
            notificationForm: {
                title: '',
                content: '',
                type: 'system'
            }
        }
    },
    computed: {
        // 过滤和排序后的用户（不分页）
        processedUsers() {
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
            if (this.sortKey) {
                filtered = [...filtered].sort((a, b) => {
                    const aValue = a[this.sortKey];
                    const bValue = b[this.sortKey];
                    if (this.sortDirection === 'asc') {
                        return aValue < bValue ? -1 : 1;
                    } else {
                        return aValue > bValue ? -1 : 1;
                    }
                });
            }
            return filtered;
        },
        // 分页后的用户
        filteredUsers() {
            const start = (this.currentPage - 1) * this.pageSize;
            const end = start + this.pageSize;
            return this.processedUsers.slice(start, end);
        },
        totalPages() {
            return Math.ceil(this.processedUsers.length / this.pageSize) || 1;
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

                const response = await api.admin.users.getList(params);
                // 处理响应数据
                const data = Array.isArray(response) ? response : (response?.results || []);
                
                // 映射后端字段到前端字段
                this.users = data.map(user => ({
                    id: user.id,
                    username: user.username,
                    email: user.email,
                    phone: user.phone || '',
                    role: user.role || 'user',
                    registerDate: user.date_joined,
                    realName: user.real_name || '',
                    address: user.address || ''
                }));

                console.log('获取到用户数据:', this.users.length, '条');
            } catch (error) {
                console.error('获取用户数据失败:', error);
                this.error = '获取用户数据失败，请稍后再试';
                this.users = [];
            } finally {
                this.isLoading = false;
            }
        },

        // 添加用户
        async addUser() {
            try {
                // 转换前端字段到后端字段
                const payload = {
                    username: this.userForm.username,
                    password: this.userForm.password,
                    email: this.userForm.email,
                    phone: this.userForm.phone,
                    role: this.userForm.role,
                    real_name: this.userForm.realName,
                    address: this.userForm.address
                };
                await api.admin.users.create(payload);
                this.closeModal();
                this.fetchUsers();
            } catch (error) {
                console.error('添加用户失败:', error);
                alert('添加用户失败: ' + (error.message || '请稍后再试'));
            }
        },

        // 更新用户
        async updateUser() {
            try {
                // 转换前端字段到后端字段
                const payload = {
                    username: this.userForm.username,
                    email: this.userForm.email,
                    phone: this.userForm.phone,
                    role: this.userForm.role,
                    real_name: this.userForm.realName,
                    address: this.userForm.address
                };
                if (this.userForm.password) {
                    payload.password = this.userForm.password;
                }
                await api.admin.users.update(this.selectedUser.id, payload);
                this.closeModal();
                this.fetchUsers();
            } catch (error) {
                console.error('更新用户失败:', error);
                alert('更新用户失败: ' + (error.message || '请稍后再试'));
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

        // 重置用户密码
        async resetUserPassword(userId) {
            try {
                await api.admin.users.resetPassword(userId);
                alert('密码已重置');
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

        // 发送通知
        sendNotification(userId) {
            const user = this.users.find(u => u.id === userId);
            if (user) {
                this.selectedUser = user;
                this.notificationForm = { title: '', content: '', type: 'system' };
                this.showNotificationModal = true;
            }
        },

        // 提交通知
        async submitNotification() {
            if (!this.selectedUser || !this.notificationForm.content) return;

            try {
                await api.admin.users.sendNotification(this.selectedUser.id, {
                    message: this.notificationForm.content,
                    title: this.notificationForm.title,
                    type: this.notificationForm.type
                });
                alert('通知已发送');
                this.showNotificationModal = false;
            } catch (error) {
                console.error('发送通知失败:', error);
                alert('发送通知失败: ' + (error.message || '请稍后再试'));
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
                'admin': '管理员'
            };
            return roles[role] || role;
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
        }
    },
    mounted() {
        this.fetchUsers();
    }
}
</script>

<style scoped>
.admin-users {
    padding: 20px 40px;
    width: 100%;
    box-sizing: border-box;
}

.title {
    font-size: 24px;
    color: #333;
    margin-bottom: 20px;
    border-bottom: 2px solid #3f51b5;
    padding-bottom: 10px;
}

.top-actions {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    margin-bottom: 20px;
    gap: 20px;
}

.btn {
    padding: 8px 16px;
    border-radius: 4px;
    border: none;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    font-size: 14px;
    transition: all 0.3s;
}

.btn i {
    margin-right: 8px;
}

.btn-primary {
    background: #3f51b5;
    color: white;
}

.btn-primary:hover {
    background: #303f9f;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.btn-secondary {
    background: #f5f5f5;
    color: #333;
}

.btn-secondary:hover {
    background: #e0e0e0;
}

.btn-danger {
    background: #f44336;
    color: white;
}

.btn-danger:hover {
    background: #d32f2f;
}

.data-table-container {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
}

.data-table th,
.data-table td {
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid #eee;
}

.data-table th {
    background: #f9f9f9;
    color: #333;
    font-weight: 600;
    cursor: pointer;
    user-select: none;
}

.data-table th i {
    margin-left: 5px;
    font-size: 12px;
}

.data-table th:hover {
    background: #f0f0f0;
}

.data-table tbody tr:hover {
    background: #f9f9f9;
}

.role-badge {
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
}

.role-user {
    background: #e3f2fd;
    color: #1976d2;
}

.role-admin {
    background: #fce4ec;
    color: #c2185b;
}

.actions-cell {
    white-space: nowrap;
    display: flex;
    gap: 5px;
}

.btn-icon {
    background: none;
    border: none;
    color: #666;
    cursor: pointer;
    padding: 5px;
    border-radius: 4px;
    transition: all 0.2s;
}

.btn-icon:hover {
    background: #f0f0f0;
    color: #333;
}

.dropdown {
    position: relative;
    display: inline-block;
}

.dropdown-toggle {
    background: none;
    border: none;
    cursor: pointer;
    padding: 5px 8px;
}

.dropdown-menu {
    position: absolute;
    right: 0;
    top: 100%;
    background: white;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
    border-radius: 4px;
    padding: 5px 0;
    min-width: 150px;
    z-index: 10;
    display: none;
}

.dropdown:hover .dropdown-menu {
    display: block;
}

.dropdown-menu a {
    display: block;
    padding: 8px 15px;
    color: #333;
    text-decoration: none;
    font-size: 14px;
    cursor: pointer;
}

.dropdown-menu a:hover {
    background: #f5f5f5;
}

.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 15px;
    border-top: 1px solid #eee;
}

.modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    border-radius: 8px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    width: 100%;
    max-width: 600px;
    max-height: 90vh;
    overflow-y: auto;
}

.modal-sm {
    max-width: 400px;
}

.modal-header {
    padding: 15px 20px;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-header h2 {
    font-size: 18px;
    color: #333;
    margin: 0;
}

.close-btn {
    background: none;
    border: none;
    font-size: 24px;
    color: #999;
    cursor: pointer;
}

.close-btn:hover {
    color: #333;
}

.modal-body {
    padding: 20px;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-size: 14px;
    color: #555;
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    outline: none;
    box-sizing: border-box;
}

.form-row {
    display: flex;
    gap: 15px;
}

.form-row .form-group {
    flex: 1;
}

.form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
}

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