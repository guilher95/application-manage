from tkinter import *
from tkinter import ttk
import sqlite3

class Producto():

    db = 'database/productos.db'

    def __init__(self,root):
        self.ventana = root
        self.ventana.title("App Gestor de Productos")
        self.ventana.resizable(1,1)
        self.ventana.wm_iconbitmap('recursos/M6_P2_icon.ico')


        #creamos el contenedor del Frame principal
        frame = LabelFrame(self.ventana, text='Registrar un nuevo Producto',font=('Calibri',16,'bold'))
        frame.grid(row=0, column=0, columnspan=2,pady=20)

        #Label nombre
        self.etiqueta_nombre = Label(frame, text="Nombre: ", font=('Calibri',12))
        self.etiqueta_nombre.grid(row=1,column=0)
        #entry nombre
        self.nombre= Entry(frame, font=('Calibri',12))
        self.nombre.focus()
        self.nombre.grid(row=1,column=1)

        # Labels precio
        self.etiqueta_precio = Label(frame, text="Precio: ", font=('Calibri',12))
        self.etiqueta_precio.grid(row=2, column=0)
        # entry precio
        self.precio = Entry(frame, font=('Calibri',12))
        self.precio.grid(row=2, column=1)

        # Button añadir producto
        s = ttk.Style()
        s.configure('my.TButton', font=('Calibri',13, 'bold'))
        self.boton_añadir = ttk.Button(frame, text='Guardar Producto', command=self.add_producto, style='my.TButton')
        self.boton_añadir.grid(row=3, columnspan=2, sticky= W + E)       #W+E coords RESPONSIVE, en este aunque nuestro frame no lo es


        #Tabla de Productos (estilo personalizado)
        style = ttk.Style()
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Calibri',11))     #fuente de la tabla
        style.configure("mystyle.Treeview.Heading", font=('Calibri',13, 'bold'))                 #cabezeras
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky':'nswe'})])     #eliminamos bordes

        #Estructura de la tabla
        self.tabla = ttk.Treeview(height=20, columns=2, style="mystyle.Treeview")
        self.tabla.grid(row=4,column=0,columnspan=2)
        self.tabla.heading('#0', text="Nombre", anchor=CENTER)            #encabezado0
        self.tabla.heading('#1', text='Precio', anchor=CENTER)            #encabezado1

        #mensaje informativo para el user
        self.mensaje = Label(text='', fg='red')
        self.mensaje.grid(row=3, column=0, columnspan=2, sticky=W+E)

        #Botones de eliminar y Editar
        s = ttk.Style()
        s.configure('my.TButton', font=('Calibri', 13, 'bold'))
        boton_eliminar = ttk.Button(text='ELIMINAR', command=self.del_producto,style='my.TButton')
        boton_eliminar.grid(row=5, column=0, sticky=W+E)
        boton_editar = ttk.Button(text='EDITAR', command=self.edit_producto,style='my.TButton')
        boton_editar.grid(row=5,column=1, sticky=W+E)

        self.get_productos()

    def db_consultas(self,consulta, parametros=()):
        with sqlite3.connect(self.db) as con:
            cursor= con.cursor()
            resultado = cursor.execute(consulta,parametros)
            con.commit()
        return resultado

    def get_productos(self):
        registros_tabla = self.tabla.get_children()
        for fila in registros_tabla:                                                                          #limpiamos todos los datos
            self.tabla.delete(fila)

        query = 'SELECT * FROM producto ORDER BY nombre DESC'
        registros_db = self.db_consultas(query)                                                                #hacemos la llamada el metodo consultas
        for fila in registros_db:                                                                              #listamos datos
            print(fila) #verificamos que se imprime en la consola
            self.tabla.insert('',0, text=fila[1],values = fila[2])                                             #accedo a mi objeto tabla y lo inserto en ella,(sin titulo,posicion 0,

    def validacion_nombre(self):
        nombre_introducido_por_usuario = self.nombre.get()                                                     #capturo el contenido
        return len(nombre_introducido_por_usuario) != 0                                                        #comprobamos que no esta vacio
    def validacion_precio(self):
        precio_introducido_por_usuario = self.precio.get()
        return len(precio_introducido_por_usuario) != 0

    def add_producto(self):
        if self.validacion_nombre() and self.validacion_precio():
            query = 'INSERT INTO producto VALUES (NULL, ?, ?)'                                                #Consulta SQL (sin datos)
            parametros = (self.nombre.get(), self.precio.get())                                               #Parametros de consulta
            self.db_consultas(query,parametros)
            print("Datos guardados en la BBDD")
            self.mensaje['text'] = 'Producto {} añadido con éxito'.format(self.nombre.get())
            self.nombre.delete(0,END)                                                                          #limpiamos nuestro entry
            self.precio.delete(0,END)

        elif self.validacion_nombre() and self.validacion_precio() == False:
            print("El precio es obligatorio")
        elif self.validacion_nombre() == False and self.validacion_precio():
            print("El nombre es obligatorio")
        else:
            print("El nombre y el precio son obligatorios")

        self.get_productos() #siempre que añadamos un producto se realiza una consulta al db

    def del_producto(self):
        #debug
        #print(self.tabla.item(self.tabla.selection()))
        #print(self.tabla.item(self.tabla.selection())['text'])
        #print(self.tabla.item(self.tabla.selection())['values'])
        #print(self.tabla.item(self.tabla.selection())['values'][0])

        self.mensaje['text'] = ''
        try:
            self.tabla.item(self.tabla.selection())['text'][0]
        except IndexError as e:
            self.mensaje['text'] = 'Por favor selecione un producto'
            return
        self.mensaje['text'] = ''
        nombre = self.tabla.item(self.tabla.selection())['text']
        query = 'DELETE FROM producto WHERE nombre = ?'
        self.db_consultas(query,(nombre,))
        self.mensaje['text'] = 'Producto {} eliminado con éxito'.format(nombre)
        self.get_productos()

    def edit_producto(self):
        self.mensaje['text'] = ''
        try:
            self.tabla.item(self.tabla.selection())['text'][0]
        except IndexError as e:
            self.mensaje['text'] = 'Por favor selecione un producto'
            return

        nombre = self.tabla.item(self.tabla.selection())['text']
        old_precio= self.tabla.item(self.tabla.selection())['values'][0]

                            ######   POP UP 1    #####
        self.ventana_editar = Toplevel()
        self.ventana_editar.title = 'Editar Producto'
        self.ventana_editar.resizable(1,1)
        self.ventana_editar.wm_iconbitmap('recursos/M6_P2_icon.ico')

        titulo = Label(self.ventana_editar, text="Edicion de Productos", font=('Calibri',23,'bold'))
        titulo.grid(column=0,row=0)
        #contenedor frame de la nueva ventana
        frame_ep = LabelFrame(self.ventana_editar, text="Editar el siguiente Producto", font=('Calibri',13,'bold'))
        frame_ep.grid(row=1, column=0, columnspan=20, pady=20)

        #       Label  nombre antiguo  Entry
        self.etiqueta_nombre_antiguo = Label(frame_ep, text= "Nombre antiguo: ", font=('Calibri',12))
        self.etiqueta_nombre_antiguo.grid(row=2, column=0)
        self.input_nombre_antiguo = Entry(frame_ep, textvariable=StringVar(self.ventana_editar, value=nombre), state='readonly', font=('Calibri',12))
        self.input_nombre_antiguo.grid(row=2,column=1)


        #       Label  nombre nuevo   Entry
        self.etiqueta_nombre_nuevo = Label(frame_ep, text="Nombre nuevo: ", font=('Calibri',12))
        self.etiqueta_nombre_nuevo.grid(row=3,column=0)
        self.input_nombre_nuevo = Entry(frame_ep, font=('Calibri',12))
        self.input_nombre_nuevo.grid(row=3, column=1)
        self.input_nombre_nuevo.focus()


        #      Label precio antiguo    Entry
        self.etiqueta_precio_antiguo = Label(frame_ep,text="Precio antiguo: ", font=('Calibri',12))
        self.etiqueta_precio_antiguo.grid(row=4, column=0)
        self.input_precio_antiguo= Entry(frame_ep, textvariable=StringVar(self.ventana_editar, value=old_precio),state='readonly', font=('Calibri',12))
        self.input_precio_antiguo.grid(row=4,column=1)


        #       Label precio nuevo    Entry
        self.etiqueta_precio_nuevo = Label(frame_ep, text="Precio nuevo: ", font=('Calibri',12))
        self.etiqueta_precio_nuevo.grid(row=5, column=0)
        self.input_precio_nuevo= Entry(frame_ep, font=('Calibri',12))
        self.input_precio_nuevo.grid(row=5, column=1)

        ###  ACTUALIZAR PRODUCTO ##
        s = ttk.Style()
        s.configure('my.TButton', font=('Calibri', 12, 'bold'))
        self.boton_actualizar = ttk.Button(frame_ep, text="Actualizar Producto", style='my.TButton', command=lambda:
        self.actualizar_producto(self.input_nombre_nuevo.get(),
        self.input_nombre_antiguo.get(),
        self.input_precio_nuevo.get(),
        self.input_precio_antiguo.get()))

        self.boton_actualizar.grid(row=6, columnspan=2, sticky=W+E)


    def actualizar_producto(self, nuevo_nombre,antiguo_nombre,nuevo_precio, antiguo_precio):
        producto_modificado = False
        query = 'UPDATE producto SET nombre = ?, precio = ? WHERE nombre = ? AND precio = ?'
        if nuevo_nombre != '' and nuevo_precio != '':
            parametros = (nuevo_nombre, nuevo_precio, antiguo_nombre, antiguo_precio)
            producto_modificado = True
        elif nuevo_nombre != '' and nuevo_precio == '':                                             #si se deja vacio el precio se matiene el precio anterior
            parametros = (nuevo_nombre, antiguo_precio,antiguo_nombre, antiguo_precio)
            producto_modificado =True
        elif nuevo_nombre == '' and nuevo_precio != '':                                             #si se deja  vacio nombre se mantiene el nombre anterior
            parametros = (antiguo_nombre,nuevo_precio,antiguo_nombre,antiguo_precio)
            producto_modificado = True
        if (producto_modificado):
            self.db_consultas(query,parametros)
            self.ventana_editar.destroy()
            self.mensaje['text'] = 'El producto {} ha sido actualizado con éxito'.format(antiguo_nombre)
            self.get_productos()
        else:
            self.ventana_editar.destroy()
            self.mensaje['text'] = 'El producto {} NO ha sido actualizado'.format(antiguo_nombre)






if __name__ == '__main__':
    root = Tk()                                                   #creamos instancia de nuestra ventana (la principal root pero da igual el nombre)
    app = Producto(root)                                          #creo el objeto de Producto (app) y le paso como parametro root (que es la ventana)
    root.mainloop()                                               #el loop es para mantener la ventana en un bucle hasta que reciba una orden