#!/usr/bin/env python3
# AxonOS/platform/core-services/resource-manager/gpu_setup.py
# -----------------------------------------------------------------
# Copyright (c) 2024 Abdullah -- Axon OS Project (AGPL-3.0)
# Purpose: Automatic GPU setup -- Real hardware, VMware, VirtualBox,
#          WSL2, Docker, CPU-only. Bilingual: English + Arabic.
# Usage:
#   python3 gpu_setup.py              -- auto setup (English)
#   python3 gpu_setup.py --ar         -- auto setup (Arabic)
#   python3 gpu_setup.py --check      -- check only
# -----------------------------------------------------------------

import os, sys, subprocess, logging, platform

LOG_DIR = os.path.expanduser("~/.axonos/logs")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(filename=os.path.join(LOG_DIR, "gpu_setup.log"),
    level=logging.INFO, format="%(asctime)s [GPUSetup] %(message)s")
log = logging.getLogger("axon.gpu_setup")

G="\033[0;32m"; R="\033[0;31m"; Y="\033[1;33m"; C="\033[0;36m"
B="\033[1m"; D="\033[2m"; NC="\033[0m"

def ok(m):   print(f"  {G}checkmark{NC}  {m}"); log.info("OK: %s", m)
def warn(m): print(f"  {Y}warn{NC}  {m}");  log.warning("WARN: %s", m)
def info(m): print(f"  {C}>{NC}  {m}");     log.info("INFO: %s", m)
def tip(m):  print(f"  {B}Tip:{NC} {m}")

ok.__doc__   = "print green checkmark"
warn.__doc__ = "print yellow warning"

# Replace placeholder symbols
def ok(m):
    print(f"  \033[0;32m\u2713\033[0m  {m}"); log.info("OK: %s", m)
def warn(m):
    print(f"  \033[1;33m\u26a0\033[0m  {m}"); log.warning("WARN: %s", m)
def info(m):
    print(f"  \033[0;36m\u2192\033[0m  {m}"); log.info("INFO: %s", m)
def tip(m):
    print(f"  \033[1m[Tip]\033[0m {m}")


# == Translations ===================================================

EN = {
    "title":       "Axon OS -- GPU Auto-Setup",
    "detecting":   "Detecting environment...",
    "env_label":   "Environment",
    "scanning":    "Scanning GPU hardware...",
    "no_gpu":      "No dedicated GPU",
    "cpu_mode":    "CPU-only mode...",
    "cpu_ready":   "PyTorch {ver} -- CPU training ready",
    "device":      "Training device",
    "backend":     "Backend",
    "env":         "Environment",
    "cuda_ready":  "CUDA ready -- {name}",
    "rocm_ready":  "ROCm ready",
    "mps_ready":   "Apple MPS ready -- no extra install needed",
    "wsl_ready":   "CUDA ready in WSL2: {name}",
    "nvml_ok":     "nvidia-ml-py installed (GPU monitoring)",
    "nvml_fail":   "nvidia-ml-py install failed",
    "nvml_exists": "NVIDIA monitoring library ready",
    "torch_no_cuda":  "PyTorch installed without CUDA",
    "torch_cuda_tip": "To enable: pip install torch --index-url https://download.pytorch.org/whl/cu121",
    "rocm_manual": "ROCm requires manual installation",
    "rocm_cmd":    "pip install torch --index-url https://download.pytorch.org/whl/rocm5.6",
    "intel_ok":    "Intel GPU library installed",
    "intel_fail":  "Intel GPU library failed -- CPU fallback",
    "intel_ready": "Intel GPU library ready",
    "mps_upgrade": "MPS not available -- upgrade PyTorch",
    "wsl_driver":  "Install NVIDIA Windows driver for CUDA in WSL2",
    "wsl_url":     "nvidia.com/Download/index.aspx",
    "cpu_install": "Install manually: pip install torch",

    # VM guidance
    "vmw_title":   "Detected: VMware Player",
    "vmw_no_cuda": "VMware Player does not support CUDA directly.",
    "vmw_options": "To enable GPU -- 3 options:",
    "vmw_opt1":    "1  VMware Workstation Pro:",
    "vmw_opt1d":   "   VM Settings -> Add -> PCI Device -> GPU",
    "vmw_opt2":    "2  WSL2 on Windows:",
    "vmw_opt2d":   "   wsl --install  (CUDA works automatically)",
    "vmw_opt3":    "3  Install Axon OS on real hardware:",
    "vmw_opt3d":   "   GPU auto-detected and enabled",
    "vmw_now":     "Now: CPU mode -- system fully operational",

    "vbox_title":  "Detected: VirtualBox",
    "vbox_no_gpu": "VirtualBox does not support GPU Passthrough for CUDA.",
    "vbox_opt1":   "1  Switch to VMware Workstation Pro",
    "vbox_opt2":   "2  Install Axon OS directly on hardware",
    "vbox_now":    "Now: CPU mode -- system fully operational",

    "wsl2_title":  "Detected: WSL2",
    "wsl2_ok":     "WSL2 supports CUDA fully!",
    "wsl2_tip":    "Make sure NVIDIA Driver is installed on Windows",

    "docker_title": "Detected: Docker Container",
    "docker_tip":  "To enable GPU: docker run --gpus all ...",

    "env_real":     "Real hardware",
    "env_vmw_pro":  "VMware Pro + GPU Passthrough",
    "env_vmw_pl":   "VMware Player",
    "env_vbox":     "VirtualBox",
    "env_wsl2":     "WSL2 (Windows)",
    "env_docker":   "Docker Container",
    "env_vm":       "Virtual machine",
}

AR = {
    "title":       "Axon OS -- اعداد GPU تلقائي",
    "detecting":   "جاري الكشف عن البيئة...",
    "env_label":   "البيئة",
    "scanning":    "فحص كرت الشاشة...",
    "no_gpu":      "لا يوجد كرت شاشة مخصص",
    "cpu_mode":    "وضع CPU فقط...",
    "cpu_ready":   "PyTorch {ver} -- التدريب على CPU جاهز",
    "device":      "جهاز التدريب",
    "backend":     "Backend",
    "env":         "البيئة",
    "cuda_ready":  "CUDA جاهز -- {name}",
    "rocm_ready":  "ROCm جاهز",
    "mps_ready":   "Apple MPS جاهز -- لا يحتاج تثبيت اضافي",
    "wsl_ready":   "CUDA جاهز في WSL2: {name}",
    "nvml_ok":     "nvidia-ml-py مثبت (مراقبة GPU)",
    "nvml_fail":   "فشل تثبيت nvidia-ml-py",
    "nvml_exists": "مكتبة مراقبة NVIDIA جاهزة",
    "torch_no_cuda":  "PyTorch مثبت بدون دعم CUDA",
    "torch_cuda_tip": "للتفعيل: pip install torch --index-url https://download.pytorch.org/whl/cu121",
    "rocm_manual": "ROCm يحتاج تثبيت يدوي",
    "rocm_cmd":    "pip install torch --index-url https://download.pytorch.org/whl/rocm5.6",
    "intel_ok":    "مكتبة Intel GPU مثبتة",
    "intel_fail":  "فشل تثبيت مكتبة Intel GPU -- وضع CPU",
    "intel_ready": "مكتبة Intel GPU جاهزة",
    "mps_upgrade": "MPS غير متاح -- قم بترقية PyTorch",
    "wsl_driver":  "ثبت NVIDIA Driver على Windows لتفعيل CUDA في WSL2",
    "wsl_url":     "nvidia.com/Download/index.aspx",
    "cpu_install": "ثبت يدويا: pip install torch",

    "vmw_title":   "تم الكشف: VMware Player",
    "vmw_no_cuda": "VMware Player لا يدعم CUDA مباشرة.",
    "vmw_options": "لتفعيل GPU -- 3 خيارات:",
    "vmw_opt1":    "1  VMware Workstation Pro:",
    "vmw_opt1d":   "   VM Settings -> Add -> PCI Device -> كرت الشاشة",
    "vmw_opt2":    "2  WSL2 على Windows:",
    "vmw_opt2d":   "   wsl --install  (CUDA يعمل تلقائيا)",
    "vmw_opt3":    "3  تثبيت Axon OS على جهاز حقيقي:",
    "vmw_opt3d":   "   GPU يكتشف ويفعل تلقائيا",
    "vmw_now":     "الان: CPU mode -- النظام يعمل بالكامل",

    "vbox_title":  "تم الكشف: VirtualBox",
    "vbox_no_gpu": "VirtualBox لا يدعم GPU Passthrough لـ CUDA.",
    "vbox_opt1":   "1  الانتقال لـ VMware Workstation Pro",
    "vbox_opt2":   "2  تثبيت Axon OS مباشرة على الجهاز",
    "vbox_now":    "الان: CPU mode -- النظام يعمل بالكامل",

    "wsl2_title":  "تم الكشف: WSL2",
    "wsl2_ok":     "WSL2 يدعم CUDA بالكامل!",
    "wsl2_tip":    "تاكد من تثبيت NVIDIA Driver على Windows",

    "docker_title": "تم الكشف: Docker Container",
    "docker_tip":  "لتفعيل GPU: docker run --gpus all ...",

    "env_real":     "جهاز حقيقي",
    "env_vmw_pro":  "VMware Pro + GPU Passthrough",
    "env_vmw_pl":   "VMware Player",
    "env_vbox":     "VirtualBox",
    "env_wsl2":     "WSL2",
    "env_docker":   "Docker Container",
    "env_vm":       "بيئة افتراضية",
}

# Active language (default English, --ar switches to Arabic)
T = EN


# == Environment ====================================================

class Env:
    REAL="real"; VMW_PRO="vmware_pro"; VMW_PLAYER="vmware_player"
    VBOX="virtualbox"; WSL2="wsl2"; DOCKER="docker"; VM="unknown_vm"

def detect_env() -> str:
    try:
        v = open("/proc/version").read().lower()
        if "microsoft" in v or "wsl" in v:
            return Env.WSL2
    except: pass
    if os.path.exists("/.dockerenv"):
        return Env.DOCKER
    try:
        vendor = subprocess.run(["cat","/sys/class/dmi/id/sys_vendor"],
            capture_output=True,text=True,timeout=3).stdout.strip().lower()
        product= subprocess.run(["cat","/sys/class/dmi/id/product_name"],
            capture_output=True,text=True,timeout=3).stdout.strip().lower()
        if "vmware" in vendor or "vmware" in product:
            lspci = subprocess.run(["lspci"],capture_output=True,text=True,timeout=3).stdout
            if "NVIDIA" in lspci or "Radeon" in lspci:
                return Env.VMW_PRO
            return Env.VMW_PLAYER
        if "virtualbox" in vendor or "innotek" in vendor:
            return Env.VBOX
    except: pass
    try:
        lspci = subprocess.run(["lspci"],capture_output=True,text=True,timeout=3).stdout
        if "VMware SVGA" in lspci:   return Env.VMW_PLAYER
        if "VirtualBox"  in lspci:   return Env.VBOX
        if "QEMU" in lspci:          return Env.VM
    except: pass
    return Env.REAL

def print_guidance(env: str):
    sep = f"  {C}{'='*52}{NC}"
    if env == Env.VMW_PLAYER:
        print(f"\n{sep}")
        print(f"  {B}{T['vmw_title']}{NC}")
        print(sep)
        print(f"  {Y}{T['vmw_no_cuda']}{NC}\n")
        print(f"  {B}{T['vmw_options']}{NC}\n")
        print(f"  {G}{T['vmw_opt1']}{NC}")
        print(f"  {D}{T['vmw_opt1d']}{NC}\n")
        print(f"  {G}{T['vmw_opt2']}{NC}")
        print(f"  {D}{T['vmw_opt2d']}{NC}\n")
        print(f"  {G}{T['vmw_opt3']}{NC}")
        print(f"  {D}{T['vmw_opt3d']}{NC}\n")
        print(f"  {C}{T['vmw_now']}{NC}")
        print(f"{sep}\n")
    elif env == Env.VBOX:
        print(f"\n{sep}")
        print(f"  {B}{T['vbox_title']}{NC}")
        print(sep)
        print(f"  {Y}{T['vbox_no_gpu']}{NC}\n")
        print(f"  {G}{T['vbox_opt1']}{NC}")
        print(f"  {G}{T['vbox_opt2']}{NC}\n")
        print(f"  {C}{T['vbox_now']}{NC}")
        print(f"{sep}\n")
    elif env == Env.WSL2:
        print(f"\n{sep}")
        print(f"  {B}{T['wsl2_title']}{NC}")
        print(sep)
        print(f"  {G}{T['wsl2_ok']}{NC}")
        tip(T["wsl2_tip"])
        print(f"  {D}  {T['wsl_url']}{NC}")
        print(f"{sep}\n")
    elif env == Env.DOCKER:
        print(f"\n{sep}")
        print(f"  {B}{T['docker_title']}{NC}")
        print(sep)
        tip(T["docker_tip"])
        print(f"{sep}\n")


# == Hardware Detection =============================================

def detect_hw() -> dict:
    r = {"nvidia":False,"amd":False,"intel":False,"apple":False,"name":"Unknown"}
    try:
        out = subprocess.run(["lspci"],capture_output=True,text=True,timeout=5).stdout
        for line in out.splitlines():
            if "NVIDIA" in line and ("VGA" in line or "3D" in line):
                r["nvidia"]=True; r["name"]=line.split(":")[-1].strip()
            elif ("AMD" in line or "Radeon" in line) and ("VGA" in line or "3D" in line):
                r["amd"]=True; r["name"]=line.split(":")[-1].strip()
            elif "Intel" in line and ("Iris" in line or "Arc" in line or "UHD" in line):
                r["intel"]=True; r["name"]=line.split(":")[-1].strip()
    except: pass
    try:
        if platform.system()=="Darwin" and "arm" in platform.processor().lower():
            r["apple"]=True; r["name"]=platform.processor()
    except: pass
    return r


# == Installers =====================================================

def pip_install(pkgs, idx=""):
    cmd=[sys.executable,"-m","pip","install","--quiet","--break-system-packages"]+pkgs
    if idx: cmd+=["--extra-index-url",idx]
    try:
        return subprocess.run(cmd,capture_output=True,text=True,timeout=300).returncode==0
    except: return False

def chk(pkg):
    try: __import__(pkg.replace("-","_").split("[")[0]); return True
    except: return False

def save_device(d):
    open(os.path.expanduser("~/.axonos/training_device.txt"),"w").write(d+"\n")

def save_note(n):
    open(os.path.expanduser("~/.axonos/gpu_setup_note.txt"),"w").write(n)

def setup_nvidia():
    info("Installing NVIDIA libraries...")
    if not chk("nvidia_ml_py") and not chk("pynvml"):
        if pip_install(["nvidia-ml-py"]): ok(T["nvml_ok"])
        else: warn(T["nvml_fail"])
    else:
        ok(T["nvml_exists"])
    try:
        import torch
        if torch.cuda.is_available():
            ok(T["cuda_ready"].format(name=torch.cuda.get_device_name(0)))
        else:
            warn(T["torch_no_cuda"])
            info(T["torch_cuda_tip"])
    except: pass

def setup_amd():
    info("AMD GPU -- checking ROCm...")
    try:
        import torch
        if torch.cuda.is_available(): ok(T["rocm_ready"]); return
    except: pass
    warn(T["rocm_manual"])
    info(T["rocm_cmd"])
    save_note(f"AMD GPU detected.\n{T['rocm_cmd']}\n")

def setup_intel():
    info("Intel GPU...")
    if not chk("intel_extension_for_pytorch"):
        if pip_install(["intel-extension-for-pytorch"]): ok(T["intel_ok"])
        else: warn(T["intel_fail"])
    else: ok(T["intel_ready"])

def setup_apple():
    try:
        import torch
        if torch.backends.mps.is_available(): ok(T["mps_ready"]); return
    except: pass
    warn(T["mps_upgrade"])

def setup_wsl2():
    info("WSL2 -- checking CUDA...")
    try:
        import torch
        if torch.cuda.is_available():
            ok(T["wsl_ready"].format(name=torch.cuda.get_device_name(0))); return
    except: pass
    warn(T["wsl_driver"])
    info(T["wsl_url"])

def setup_cpu():
    info(T["cpu_mode"])
    try:
        import torch; ok(T["cpu_ready"].format(ver=torch.__version__))
    except:
        if pip_install(["torch","--index-url","https://download.pytorch.org/whl/cpu"]):
            ok(T["cpu_ready"].format(ver=""))
        else:
            warn(T["cpu_install"])
    save_device("cpu")


# == Main ===========================================================

def run(check_only=False):
    print(f"\n{C}{B}╔══════════════════════════════════════════╗{NC}")
    print(f"{C}{B}║   {T['title']:<38}║{NC}")
    print(f"{C}{B}╚══════════════════════════════════════════╝{NC}\n")

    info(T["detecting"])
    env = detect_env()

    env_map = {
        Env.REAL:       f"{G}{T['env_real']}{NC}",
        Env.VMW_PRO:    f"{G}{T['env_vmw_pro']}{NC}",
        Env.VMW_PLAYER: f"{Y}{T['env_vmw_pl']}{NC}",
        Env.VBOX:       f"{Y}{T['env_vbox']}{NC}",
        Env.WSL2:       f"{G}{T['env_wsl2']}{NC}",
        Env.DOCKER:     f"{C}{T['env_docker']}{NC}",
        Env.VM:         f"{Y}{T['env_vm']}{NC}",
    }
    print(f"  {T['env_label']}: {env_map.get(env, env)}")

    if env in [Env.VMW_PLAYER, Env.VBOX, Env.WSL2, Env.DOCKER]:
        print_guidance(env)

    info(T["scanning"])
    hw = detect_hw()

    if hw["nvidia"]:  print(f"  {G}\u25cf{NC}  NVIDIA: {hw['name']}")
    elif hw["amd"]:   print(f"  {Y}\u25cf{NC}  AMD: {hw['name']}")
    elif hw["intel"]: print(f"  {C}\u25cf{NC}  Intel: {hw['name']}")
    elif hw["apple"]: print(f"  {C}\u25cf{NC}  Apple: {hw['name']}")
    else:             print(f"  {D}\u25cf  {T['no_gpu']}{NC}")

    if check_only: return {"env": env, **hw}
    print()

    if   env==Env.WSL2:                           setup_wsl2(); d="cuda"; b="wsl2"
    elif env==Env.VMW_PRO and hw["nvidia"]:        setup_nvidia(); d="cuda"; b="nvidia"
    elif env in [Env.VMW_PLAYER,Env.VBOX,Env.VM]:  setup_cpu(); d="cpu"; b="cpu_only"
    elif hw["nvidia"]: setup_nvidia(); d="cuda"; b="nvidia"
    elif hw["amd"]:    setup_amd();    d="cuda"; b="amd"
    elif hw["intel"]:  setup_intel();  d="xpu";  b="intel"
    elif hw["apple"]:  setup_apple();  d="mps";  b="apple"
    else:              setup_cpu();    d="cpu";  b="cpu_only"

    save_device(d)
    print(f"\n{G}{'='*44}{NC}")
    print(f"  {T['device']}: {G}{d}{NC}")
    print(f"  {T['backend']}: {G}{b}{NC}")
    print(f"  {T['env']}: {env}")
    print(f"{G}{'='*44}{NC}\n")
    log.info("Setup complete device=%s backend=%s env=%s", d, b, env)
    return {"device": d, "backend": b, "env": env}

def get_saved_device():
    p = os.path.expanduser("~/.axonos/training_device.txt")
    return open(p).read().strip() if os.path.exists(p) else "cpu"

if __name__ == "__main__":
    if "--ar" in sys.argv:
        T = AR
    check_only = "--check" in sys.argv
    run(check_only=check_only)
