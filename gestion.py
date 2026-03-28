from services.producto_service import Catalogo

def menu():
    cat = Catalogo()
    while True:
        print("\n--- SISTEMA DE GESTIÓN: JOYERÍA RESPLANDOR ---")
        print("1. Añadir nuevo producto")
        print("2. Mostrar todos los productos")
        print("3. Buscar producto por nombre")
        print("4. Actualizar cantidad (Stock) o Precio")
        print("5. Eliminar producto por ID")
        print("6. Salir")
        
        opcion = input("\nSeleccione una opción: ")

        if opcion == "1":
            mod = input("Modelo: ")
            col = input("Colección: ")
            mat = input("Material: ")
            pes = input("Peso (ej. 5g): ")
            can = int(input("Cantidad: "))
            pre = float(input("Precio: "))
            cat.añadir_pieza(mod, col, mat, pes, can, pre)
            print("¡Producto añadido con éxito!")

        elif opcion == "2":
            # Requisito: Mostrar todos los productos en formato tabla
            productos = cat.obtener_todo()
            print("\n" + "="*60)
            # Definimos los encabezados con espacios fijos
            print(f"{'ID':<4} | {'MODELO':<20} | {'STOCK':<8} | {'PRECIO':<10}")
            print("-" * 60)
            
            for p in productos:
                # El símbolo <20 significa que reserva 20 espacios a la izquierda
                print(f"{p.id:<4} | {p.modelo:<20} | {p.cantidad:<8} | ${p.precio:<10}")
            
            print("="*60 + "\n")

        elif opcion == "3":
            # Requisito: Buscar y mostrar por nombre
            nombre = input("Ingrese el nombre a buscar: ")
            resultados = cat.buscar_por_nombre(nombre)
            if resultados:
                for r in resultados:
                    print(f"Encontrado: ID {r.id} - {r.modelo} (${r.precio})")
            else:
                print("No se encontraron coincidencias.")

        elif opcion == "4":
            # Requisito: Actualizar cantidad o precio
            id_act = int(input("ID del producto a modificar: "))
            print("1. Actualizar Cantidad\n2. Actualizar Precio")
            sub_opc = input("Elija: ")
            if sub_opc == "1":
                nueva_can = int(input("Nueva cantidad: "))
                cat.actualizar_stock(id_act, nueva_can)
            elif sub_opc == "2":
                nuevo_pre = float(input("Nuevo precio: "))
                # Nota: Deberás añadir el método actualizar_precio en inventario.py
                cat.actualizar_precio(id_act, nuevo_pre)
            print("¡Dato actualizado!")

        elif opcion == "5":
            # Requisito: Eliminar por ID
            id_del = int(input("ID del producto a eliminar: "))
            cat.eliminar_producto(id_del)
            print(f"Producto {id_del} eliminado.")

        elif opcion == "6":
            print("Saliendo del sistema...")
            break

if __name__ == "__main__":
    menu()