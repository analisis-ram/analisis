    # ==========================================================
    # 5. SOLAPAS TIPO EXCEL
    # ==========================================================
    st.markdown("---")
    st.subheader("📑 Solapas del Excel")

    # --------------------------
    # Definición de filas Balance
    # --------------------------
    filas_balance = [
        ("Inmovilizado Inmaterial", lambda d: v(d, '00102') or v(d, '00101')),
        ("Inmovilizado Material", lambda d: v(d, '00111')),
        ("Inversiones inmobiliarias", lambda d: v(d, '00115')),
        ("Inversiones financieras a largo plazo", lambda d: v(d, '00126')),
        ("Activos por Impuesto Diferido", lambda d: v(d, '00134')),
        ("INMOVILIZADO", lambda d: v(d, '00101')),
        ("Existencias", lambda d: v(d, '00138')),
        ("Clientes", lambda d: v(d, '00150')),
        ("Hacienda pública", lambda d: v(d, '00157')),
        ("Inv. Finan. C.P.", lambda d: v(d, '00168')),
        ("Deudores varios", lambda d: v(d, '00159')),
        ("Disponible en Caja y Bancos", lambda d: v(d, '00177')),
        ("Periodificaciones C.P.", lambda d: v(d, '00176')),
        ("REALIZABLE + DISPONIBLE", lambda d: v(d, '00149') + v(d, '00168') + v(d, '00159')),
        ("TOTAL ACTIVO", lambda d: v(d, '00180')),
        ("Capital y Reservas", lambda d: v(d, '00187') + v(d, '00191') + v(d, '00195')),
        ("Resultado del ejercicio", lambda d: v(d, '00199')),
        ("Subvenciones y Provisiones", lambda d: v(d, '00209')),
        ("CAPITALES PROPIOS", lambda d: v(d, '00185')),
        ("Deuda a Largo Plazo", lambda d: v(d, '00216')),
        ("CAPITALES PERMANENTES", lambda d: v(d, '00185') + v(d, '00216')),
        ("Acreedores", lambda d: v(d, '00249') or v(d, '00244')),
        ("Proveedores", lambda d: v(d, '00240')),
        ("Otras deudas a Corto Plazo", lambda d: v(d, '00237')),
        ("Acreedores Arrendamiento Financiero", lambda d: v(d, '00234')),
        ("Deuda a Corto Plazo (Bancos)", lambda d: v(d, '00233')),
        ("DEUDA A CORTO PLAZO", lambda d: v(d, '00231')),
        ("TOTAL PASIVO", lambda d: v(d, '00252')),
    ]

    # --------------------------
    # Definición de filas Explotación
    # --------------------------
    filas_explotacion = [
        ("CIFRA DE NEGOCIO", lambda d: v(d, '00255')),
        ("Aprovisionamientos", lambda d: abs(v(d, '00260'))),
        ("COMPRAS CONSUMIDAS", lambda d: abs(v(d, '00260'))),
        ("Margen Bruto", lambda d: v(d, '00255') - abs(v(d, '00260'))),
        ("Gastos de Personal", lambda d: abs(v(d, '00270'))),
        ("Otros Gastos de Explotación", lambda d: abs(v(d, '00279'))),
        ("Dotación Amortizaciones", lambda d: abs(v(d, '00284'))),
        ("GASTOS DE ESTRUCTURA", lambda d: abs(v(d, '00270')) + abs(v(d, '00279')) + abs(v(d, '00284'))),
        ("Resultado de Explotación", lambda d: v(d, '00296')),
        ("Gastos Financieros", lambda d: abs(v(d, '00305'))),
        ("Resultado Actividades Ordinarias", lambda d: v(d, '00296') - abs(v(d, '00305'))),
        ("Impuesto Sociedades", lambda d: abs(v(d, '00326'))),
        ("RESULTADO NETO", lambda d: v(d, '00500')),
        ("Cash-Flow", lambda d: v(d, '00500') + abs(v(d, '00284'))),
    ]

    # --------------------------
    # Bal: resumen en miles de €
    # --------------------------
    filas_bal = [
        ("INMOVILIZADO", lambda d: v(d, '00101') / 1000),
        ("EXISTENCIAS", lambda d: v(d, '00138') / 1000),
        ("REALIZABLE", lambda d: (v(d, '00149') + v(d, '00168') + v(d, '00159')) / 1000),
        ("DISPONIBLE", lambda d: v(d, '00177') / 1000),
        ("TOTAL ACTIVO", lambda d: v(d, '00180') / 1000),
        ("CAPITAL PROPIO", lambda d: v(d, '00185') / 1000),
        ("DEUDAS A LARGO", lambda d: v(d, '00216') / 1000),
        ("DEUDAS A CORTO", lambda d: v(d, '00231') / 1000),
        ("TOTAL PASIVO", lambda d: v(d, '00252') / 1000),
    ]

    # --------------------------
    # Exp: resumen en miles de €
    # --------------------------
    filas_exp = [
        ("VENTAS", lambda d: v(d, '00255') / 1000),
        ("- COSTE DE VENTAS", lambda d: abs(v(d, '00260')) / 1000),
        ("MARGEN BRUTO", lambda d: (v(d, '00255') - abs(v(d, '00260'))) / 1000),
        ("- GTOS. PERSONAL", lambda d: abs(v(d, '00270')) / 1000),
        ("- GTOS. DIVERSOS", lambda d: abs(v(d, '00279')) / 1000),
        ("- GTOS. FINANCIEROS", lambda d: abs(v(d, '00305')) / 1000),
        ("- AMORTIZACIONES", lambda d: abs(v(d, '00284')) / 1000),
        ("Resultado del Negocio", lambda d: v(d, '00296') / 1000),
        ("Resultado Neto", lambda d: v(d, '00500') / 1000),
    ]

    # --------------------------
    # Umbral aproximado
    # --------------------------
    def tabla_umbral(datos):
        rows = []
        for d in datos:
            ingresos = v(d, '00255')
            aprov = abs(v(d, '00260'))
            cf = abs(v(d, '00270')) + abs(v(d, '00284')) + abs(v(d, '00305'))

            mc = (1 - (aprov / ingresos)) if ingresos else 0
            umbral = (cf / mc) if mc > 0 else None
            cobertura = (ingresos / umbral) if umbral and umbral > 0 else None

            rows.append({
                "Año": d["year_label"],
                "Ventas reales": ingresos,
                "Costes fijos aprox.": cf,
                "Margen contribución": mc,
                "Umbral ventas aprox.": umbral,
                "Cobertura": cobertura
            })

        return pd.DataFrame(rows)

    # --------------------------
    # Fondo de maniobra por año
    # --------------------------
    def tabla_fonman(d):
        ingresos = v(d, '00255')
        aprov = abs(v(d, '00260'))
        existencias = v(d, '00138')
        clientes = v(d, '00150')
        proveedores = v(d, '00240')

        dias_almacen = (existencias / aprov * 365) if aprov else 0
        dias_cobro = (clientes / ingresos * 365) if ingresos else 0
        dias_pago = (proveedores / aprov * 365) if aprov else 0
        ciclo_maduracion = dias_almacen + dias_cobro

        gastos_diarios = (
            aprov + abs(v(d, '00270')) + abs(v(d, '00279'))
        ) / 365 if 365 else 0

        fm_necesario = gastos_diarios * ciclo_maduracion
        fin_proveedores = (proveedores / 365 * dias_pago) if dias_pago else 0

        capitales_permanentes = v(d, '00185') + v(d, '00216')
        fin_capitales_permanentes = capitales_permanentes - v(d, '00101')

        resultado = fm_necesario - fin_proveedores - fin_capitales_permanentes

        return pd.DataFrame([
            {"Concepto": "Días almacén", "Valor": dias_almacen},
            {"Concepto": "Días cobro", "Valor": dias_cobro},
            {"Concepto": "Días pago", "Valor": dias_pago},
            {"Concepto": "Ciclo de maduración", "Valor": ciclo_maduracion},
            {"Concepto": "Gastos diarios", "Valor": gastos_diarios},
            {"Concepto": "Fondo de maniobra necesario", "Valor": fm_necesario},
            {"Concepto": "Financiado por proveedores", "Valor": fin_proveedores},
            {"Concepto": "Financiado con capitales permanentes", "Valor": fin_capitales_permanentes},
            {"Concepto": "Superávit / Déficit fondo de maniobra", "Valor": resultado},
        ])

    # --------------------------
    # Creación de pestañas
    # --------------------------
    tabs = st.tabs([
        "Balance",
        "Explotación",
        "Bal",
        "Exp",
        "Umbral",
        "Fon.Man.1",
        "Fon.Man.2",
        "Fon.Man.3",
    ])

    with tabs[0]:
        render_tabla("Balance comparado (euros)", filas_balance, datos_empresa)

    with tabs[1]:
        render_tabla("Explotación - Rentabilidad (euros)", filas_explotacion, datos_empresa)

    with tabs[2]:
        render_tabla("Bal - Resumen balance (miles de €)", filas_bal, datos_empresa)

    with tabs[3]:
        render_tabla("Exp - Resumen cuenta resultados (miles de €)", filas_exp, datos_empresa)

    with tabs[4]:
        st.markdown("#### Umbral de rentabilidad aproximado")
        st.dataframe(
            tabla_umbral(datos_empresa).style.format({
                "Ventas reales": "{:,.2f} €",
                "Costes fijos aprox.": "{:,.2f} €",
                "Margen contribución": "{:.2%}",
                "Umbral ventas aprox.": "{:,.2f} €",
                "Cobertura": "{:.2f}"
            }),
            use_container_width=True,
            hide_index=True
        )

    with tabs[5]:
        if len(datos_empresa) >= 1:
            st.markdown(f"#### Fondo de maniobra - {datos_empresa[0]['year_label']}")
            st.dataframe(
                tabla_fonman(datos_empresa[0]).style.format({"Valor": "{:,.2f}"}),
                use_container_width=True,
                hide_index=True
            )

    with tabs[6]:
        if len(datos_empresa) >= 2:
            st.markdown(f"#### Fondo de maniobra - {datos_empresa[1]['year_label']}")
            st.dataframe(
                tabla_fonman(datos_empresa[1]).style.format({"Valor": "{:,.2f}"}),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Se necesitan al menos 2 ejercicios para esta solapa.")

    with tabs[7]:
        if len(datos_empresa) >= 3:
            st.markdown(f"#### Fondo de maniobra - {datos_empresa[2]['year_label']}")
            st.dataframe(
                tabla_fonman(datos_empresa[2]).style.format({"Valor": "{:,.2f}"}),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Se necesitan al menos 3 ejercicios para esta solapa.")