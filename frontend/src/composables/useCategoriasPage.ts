import { computed, ref } from 'vue'
import { useDataStore } from '../stores/data'
import { useToastStore } from '../stores/toast'
import type { Categoria } from '../types'

const COLORES = ['#7fdcdc', '#f58f88', '#f8db8f', '#c9bbfb', '#c9ccd6', '#f7bdd5', '#aee2bd', '#aecbf3', '#f8c9a0', '#a3dccf']

export function useCategoriasPage() {
  const data = useDataStore()
  const { push: toast } = useToastStore()
  const q = ref('')
  const verOcultas = ref(false)
  const ocultas = computed(() => data.categorias.filter((c) => c.oculto).length)
  const form = ref<Categoria | null>(null)
  const borrar = ref<Categoria | null>(null)

  const lista = computed(() =>
    data.categorias
      .filter((c) => !!c.oculto === verOcultas.value && c.nombre.toLowerCase().includes(q.value.toLowerCase()))
      .map((c) => {
        const prods = data.productos.filter((p) => p.categoriaId === c.id)
        return {
          ...c,
          cant: prods.length,
          unidades: prods.reduce((s, p) => s + p.stock, 0),
          bajos: prods.filter((p) => p.stock <= p.stockMinimo).length,
        }
      }),
  )

  const nueva = () => (form.value = { id: '', nombre: '', descripcion: '', color: COLORES[0] })
  const editar = (c: Categoria) => (form.value = { id: c.id, nombre: c.nombre, descripcion: c.descripcion, color: c.color, oculto: c.oculto })

  function alternar(c: Categoria) {
    const oculta = data.alternarOculto('categoria', c.id)
    toast(oculta ? `"${c.nombre}" oculta: sus productos no se muestran en Caja` : `"${c.nombre}" visible nuevamente`, 'info')
  }

  function guardar() {
    if (!form.value) return
    if (!form.value.nombre.trim()) return toast('El nombre es obligatorio', 'error')
    data.guardarCategoria(form.value)
    toast(form.value.id ? 'Categoría actualizada' : 'Categoría creada')
    form.value = null
  }

  function pedirBorrar(c: Categoria & { cant: number }) {
    if (c.cant > 0) return toast(`No se puede eliminar: tiene ${c.cant} producto(s) asignado(s)`, 'error')
    borrar.value = c
  }

  return { COLORES, data, q, verOcultas, ocultas, form, borrar, lista, nueva, editar, alternar, guardar, pedirBorrar, toast }
}
