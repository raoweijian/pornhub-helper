let app = new Vue({
    el: "#container",
    delimiters: ['[[', ']]'],
    data: {
        login_info: {
            data: {
                username: "",
                password: "",
                remember: true,
            },

            rules: {
                account: [{ required: true, message: '请输入账号', trigger: 'change' }],
                passwd: [{ required: true, message: '请输入密码', trigger: 'change' }],
            },
        },
    },

    created: function(){
    },

    mounted: function(){},

    methods: {
        login: function(){
            axios.post("/auth/login", this.login_info.data).then((response)=>{
                if (response.status === 200 && response.data == "ok"){
                    window.location = "/";
                }else{
                    this.$message.error(response.data);
                }
            }).catch(error => {
                this.$message.error(error.response.data.message);
            });
        },
    },

    watch: {},
});

