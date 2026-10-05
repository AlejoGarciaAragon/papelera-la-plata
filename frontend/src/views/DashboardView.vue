<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const logout = () => {
	localStorage.removeItem('access')
	localStorage.removeItem('refresh')
	router.push('/login')
}
</script>

<template>
	<main class="min-h-screen bg-[#f8fbfa] px-6 py-8 text-slate-700">
		<header class="mx-auto flex w-full max-w-6xl items-center justify-between rounded-2xl border border-teal-100/80 bg-white/90 px-5 py-4 shadow-sm sm:px-7">
			<div>
				<p class="text-xs font-semibold uppercase tracking-[0.18em] text-teal-600/70">Papelera La Plata</p>
				<h1 class="mt-1 text-2xl font-semibold tracking-tight">Dashboard</h1>
			</div>

			<button
				type="button"
				class="rounded-xl border border-rose-100 bg-rose-50 px-4 py-2 text-sm font-semibold text-rose-700 transition-colors hover:bg-rose-100 focus:outline-none focus:ring-4 focus:ring-rose-100"
				@click="logout"
			>
				Cerrar sesión
			</button>
		</header>
	</main>
</template>