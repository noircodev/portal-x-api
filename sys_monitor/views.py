from datetime import timedelta
import cpuinfo
import time
import psutil
from django.http import JsonResponse
from django.shortcuts import render
import platform
from django.views.generic import View


class SystemInfoView(View):
    def get(self, request, *args, **kwargs):
        freq = psutil.cpu_freq()
        frequency = {
            'current': f"{freq.current:.2f} MHz",
            'min': f"{freq.min:.2f} MHz",
            'max': f"{freq.max:.2f} MHz"
        }
        if platform.system() == "Linux":
            # For Python 3.8+:
            # Requires systemd
            platform_info = platform.freedesktop_os_release()
        elif platform.system() == "Darwin":
            # macOS doesn't have a direct equivalent to freedesktop_os_release
            platform_info = platform.mac_ver()
        elif platform.system() == "Windows":
            # Windows doesn't have a direct equivalent to freedesktop_os_release
            platform_info = platform.win32_ver()

        context = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "os_version": platform.version(),
            "architecture": platform.architecture(),
            "machine": platform.machine(),
            "processor": cpuinfo.get_cpu_info().get('brand_raw', 'Unknown CPU'),
            "uptime": self.get_uptime() if self.get_uptime() else "Unknown",
            "platform_image": self.get_platform_image(platform_info.get('ID')),
            "platform_info": platform_info,
            "cpu_cores": psutil.cpu_count(logical=False),
            "cpu_threads": psutil.cpu_count(logical=True),
            "cpu_freq": frequency,
            "total_ram": self.sizeof_fmt(psutil.virtual_memory().total),
            "swap_total": self.sizeof_fmt(psutil.swap_memory().total),
        }
        return render(request, "sys_monitor/system_info.html", context)

    @staticmethod
    def sizeof_fmt(num, suffix="B"):
        for unit in ["", "K", "M", "G", "T", "P"]:
            if abs(num) < 1024.0:
                return f"{num:.2f} {unit}{suffix}"
            num /= 1024.0
        return f"{num:.2f} P{suffix}"

    @staticmethod
    def get_uptime():
        seconds = time.time() - psutil.boot_time()
        td = timedelta(seconds=int(seconds))
        days = td.days
        hours, remainder = divmod(td.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{days} days, {hours} hours, {minutes} minutes"

    def get_platform_image(self, platform_id):
        if platform_id:
            return f"/static/sysmonitor/images/os/{platform_id}.svg"
        if platform.system() == "Linux":
            return "/static/sysmonitor/images/os/linux.svg"
        if platform.system() == "Darwin":
            return "/static/sysmonitor/images/os/macos.svg"
        if platform.system() == "Windows":
            return "/static/sysmonitor/images/os/windows.svg"
        return "/static/sysmonitor/images/os/default.svg"


class SystemStatsView(View):
    def get(self, request, *args, **kwargs):
        cpu_percent = psutil.cpu_percent(percpu=True)
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return JsonResponse({
            "cpu": cpu_percent,
            "memory": {
                "total": memory.total,
                "used": memory.used,
                "percent": memory.percent
            },
            "swap": {
                "total": swap.total,
                "used": swap.used,
                "percent": swap.percent
            },
            "timestamp": psutil.boot_time(),
            "platform": platform.system()
        })


class SystemStatsView(View):
    def get(self, request, *args, **kwargs):
        cpu_percent = psutil.cpu_percent(percpu=True)
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return JsonResponse({
            "cpu": cpu_percent,
            "timestamp": time.time(),
            "memory": {
                "total": mem.total,
                "used": mem.used,
                "available": mem.available,
                "percent": mem.percent
            },
            "swap": {
                "total": swap.total,
                "used": swap.used,
                "free": swap.free,
                "percent": swap.percent
            },
            "platform": platform.system(),
            "uptime": time.time() - psutil.boot_time()
        })


system_stats_view = SystemStatsView.as_view()
system_info_view = SystemInfoView.as_view()
