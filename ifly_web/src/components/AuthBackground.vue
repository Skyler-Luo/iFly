<template>
    <div class="auth-background">
        <div class="stars"></div>
        <div class="twinkling-stars"></div>
        <div class="shooting-star"></div>
        <div class="shooting-star-2"></div>
        <div class="moon"></div>
        <div class="flying-planes">
            <div class="plane plane-1">✈</div>
            <div class="plane plane-2">✈</div>
            <div class="plane plane-3">✈</div>
            <div class="plane plane-4">✈</div>
            <div class="cloud cloud-1"></div>
            <div class="cloud cloud-2"></div>
            <div class="cloud cloud-3"></div>
        </div>
        <slot></slot>
    </div>
</template>

<script>
export default {
    name: 'AuthBackground'
}
</script>

<style scoped>
@keyframes float {
    0% {
        transform: translateY(0px);
    }

    50% {
        transform: translateY(-20px);
    }

    100% {
        transform: translateY(0px);
    }
}

@keyframes flying {
    0% {
        transform: translateX(0) translateY(0) rotate(0deg);
    }

    50% {
        transform: translateX(200px) translateY(-50px) rotate(5deg);
    }

    100% {
        transform: translateX(0) translateY(0) rotate(0deg);
    }
}

@keyframes cloud-drift {
    0% {
        transform: translateX(-150%);
    }

    100% {
        transform: translateX(150%);
    }
}

@keyframes twinkling {
    0% {
        opacity: 0.3;
    }

    50% {
        opacity: 1;
    }

    100% {
        opacity: 0.3;
    }
}

@keyframes shooting-star {
    0% {
        transform: translateX(0) translateY(0) rotate(315deg);
        opacity: 1;
    }

    70% {
        opacity: 1;
    }

    100% {
        transform: translateX(500px) translateY(500px) rotate(315deg);
        opacity: 0;
    }
}

@keyframes sun-rays {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

@keyframes pulse-glow {
    0% {
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.8), 0 0 40px rgba(255, 255, 255, 0.6);
    }

    50% {
        box-shadow: 0 0 30px rgba(255, 255, 255, 0.9), 0 0 60px rgba(255, 255, 255, 0.7), 0 0 80px rgba(255, 255, 255, 0.4);
    }

    100% {
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.8), 0 0 40px rgba(255, 255, 255, 0.6);
    }
}

.auth-background {
    width: 100%;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #0a1128 0%, #1a2980 50%, #304090 100%);
    position: relative;
    overflow: hidden;
}

.auth-background::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle at center, rgba(32, 42, 128, 0.1) 0%, rgba(10, 17, 40, 0.6) 70%, rgba(10, 17, 40, 0.9) 100%);
    z-index: 0;
}

.stars {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 1;
}

.stars::before {
    content: '';
    position: absolute;
    width: 100%;
    height: 100%;
    background-image:
        radial-gradient(1px 1px at 25% 10%, white 1px, transparent 0),
        radial-gradient(1px 1px at 50% 25%, white 1px, transparent 0),
        radial-gradient(1px 1px at 75% 30%, white 1px, transparent 0),
        radial-gradient(1.5px 1.5px at 15% 40%, white 1px, transparent 0),
        radial-gradient(1.5px 1.5px at 60% 45%, white 1px, transparent 0),
        radial-gradient(1px 1px at 30% 60%, white 1px, transparent 0),
        radial-gradient(1.5px 1.5px at 70% 65%, white 1px, transparent 0),
        radial-gradient(2px 2px at 85% 80%, white 1px, transparent 0),
        radial-gradient(1px 1px at 10% 85%, white 1px, transparent 0),
        radial-gradient(1.5px 1.5px at 45% 95%, white 1px, transparent 0);
    background-size: 250px 250px;
    background-repeat: repeat;
}

.stars::after {
    content: '';
    position: absolute;
    width: 100%;
    height: 100%;
    background-image:
        radial-gradient(2px 2px at 10% 20%, rgba(255, 255, 255, 0.9) 1px, transparent 0),
        radial-gradient(2px 2px at 35% 35%, rgba(255, 255, 255, 0.9) 1px, transparent 0),
        radial-gradient(2.5px 2.5px at 55% 15%, rgba(255, 255, 255, 0.9) 1px, transparent 0),
        radial-gradient(2px 2px at 77% 38%, rgba(255, 255, 255, 0.9) 1px, transparent 0),
        radial-gradient(2.5px 2.5px at 25% 65%, rgba(255, 255, 255, 0.9) 1px, transparent 0),
        radial-gradient(2px 2px at 65% 60%, rgba(255, 255, 255, 0.9) 1px, transparent 0),
        radial-gradient(2.5px 2.5px at 90% 75%, rgba(255, 255, 255, 0.9) 1px, transparent 0),
        radial-gradient(2px 2px at 20% 90%, rgba(255, 255, 255, 0.9) 1px, transparent 0),
        radial-gradient(2.5px 2.5px at 50% 85%, rgba(255, 255, 255, 0.9) 1px, transparent 0);
    background-size: 350px 350px;
    background-repeat: repeat;
}

.twinkling-stars {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}

.twinkling-stars::before {
    content: '';
    position: absolute;
    top: 15%;
    left: 25%;
    width: 3px;
    height: 3px;
    border-radius: 50%;
    background-color: white;
    box-shadow: 0 0 5px 1px rgba(255, 255, 255, 0.8);
    animation: twinkling 2s infinite ease-in-out;
}

.twinkling-stars::after {
    content: '';
    position: absolute;
    top: 65%;
    left: 80%;
    width: 3px;
    height: 3px;
    border-radius: 50%;
    background-color: white;
    box-shadow: 0 0 5px 1px rgba(255, 255, 255, 0.8);
    animation: twinkling 3s infinite ease-in-out;
    animation-delay: 0.5s;
}

.shooting-star {
    position: absolute;
    top: 20%;
    left: 80%;
    width: 100px;
    height: 2px;
    background: linear-gradient(to right, rgba(255, 255, 255, 0), rgba(255, 255, 255, 1));
    border-radius: 50%;
    animation: shooting-star 6s infinite ease-out;
    animation-delay: 2s;
    z-index: 1;
    opacity: 0;
}

.shooting-star::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.8);
    box-shadow: 0 0 10px 2px rgba(255, 255, 255, 0.8);
}

.shooting-star-2 {
    position: absolute;
    top: 10%;
    left: 30%;
    width: 150px;
    height: 2px;
    background: linear-gradient(to right, rgba(255, 255, 255, 0), rgba(255, 255, 255, 1));
    border-radius: 50%;
    animation: shooting-star 8s infinite ease-out;
    animation-delay: 5s;
    z-index: 1;
    opacity: 0;
}

.shooting-star-2::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.8);
    box-shadow: 0 0 10px 2px rgba(255, 255, 255, 0.8);
}

.moon {
    position: absolute;
    top: 50px;
    right: 100px;
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(240, 240, 255, 0.8) 100%);
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.8),
        0 0 40px rgba(255, 255, 255, 0.6);
    z-index: 1;
    animation: pulse-glow 5s infinite ease-in-out;
}

.moon::before {
    content: '';
    position: absolute;
    top: 15px;
    left: 15px;
    width: 15px;
    height: 15px;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.4);
    box-shadow: inset 0 0 5px rgba(255, 255, 255, 0.1);
}

.moon::after {
    content: '';
    position: absolute;
    bottom: 20px;
    right: 25px;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.3);
    box-shadow: inset 0 0 5px rgba(255, 255, 255, 0.1);
}

.flying-planes {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 2;
}

.plane {
    position: absolute;
    font-size: 24px;
    color: rgba(255, 255, 255, 0.7);
    text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
    transform-style: preserve-3d;
    transition: all 0.3s ease;
}

.plane-1 {
    top: 20%;
    left: 10%;
    animation: flying 20s infinite ease-in-out;
    font-size: 30px;
}

.plane-2 {
    top: 30%;
    left: 70%;
    animation: flying 25s infinite ease-in-out reverse;
    animation-delay: -10s;
}

.plane-3 {
    top: 60%;
    left: 30%;
    animation: flying 30s infinite ease-in-out;
    animation-delay: -5s;
    font-size: 28px;
}

.plane-4 {
    top: 80%;
    left: 60%;
    animation: flying 22s infinite ease-in-out reverse;
    animation-delay: -15s;
}

.cloud {
    position: absolute;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 50px;
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(1px);
}

.cloud:before,
.cloud:after {
    content: '';
    position: absolute;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 50%;
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
}

.cloud-1 {
    width: 120px;
    height: 45px;
    top: 40%;
    left: 50%;
    animation: cloud-drift 30s infinite linear;
}

.cloud-1:before {
    width: 70px;
    height: 70px;
    top: -35px;
    left: 15px;
}

.cloud-1:after {
    width: 60px;
    height: 60px;
    top: -25px;
    left: 55px;
}

.cloud-2 {
    width: 100px;
    height: 35px;
    top: 25%;
    left: 40%;
    animation: cloud-drift 25s infinite linear;
    animation-delay: -15s;
}

.cloud-2:before {
    width: 60px;
    height: 60px;
    top: -30px;
    left: 10px;
}

.cloud-2:after {
    width: 50px;
    height: 50px;
    top: -20px;
    left: 45px;
}

.cloud-3 {
    width: 140px;
    height: 55px;
    top: 60%;
    left: 30%;
    animation: cloud-drift 35s infinite linear;
    animation-delay: -5s;
}

.cloud-3:before {
    width: 80px;
    height: 80px;
    top: -40px;
    left: 20px;
}

.cloud-3:after {
    width: 70px;
    height: 70px;
    top: -30px;
    left: 65px;
}
</style>