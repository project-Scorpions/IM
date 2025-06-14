PGDMP  "    #                }            pharmacy_db    17.4    17.4 =    r           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                           false            s           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                           false            t           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                           false            u           1262    20073    pharmacy_db    DATABASE     q   CREATE DATABASE pharmacy_db WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en-US';
    DROP DATABASE pharmacy_db;
                     postgres    false            �            1259    20163 
   audit_logs    TABLE     L  CREATE TABLE public.audit_logs (
    log_id integer NOT NULL,
    user_id integer,
    action_type character varying(50) NOT NULL,
    table_affected character varying(50),
    record_id integer,
    action_details text,
    ip_address character varying(50),
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
    DROP TABLE public.audit_logs;
       public         heap r       postgres    false            �            1259    20162    audit_logs_log_id_seq    SEQUENCE     �   CREATE SEQUENCE public.audit_logs_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ,   DROP SEQUENCE public.audit_logs_log_id_seq;
       public               postgres    false    230            v           0    0    audit_logs_log_id_seq    SEQUENCE OWNED BY     O   ALTER SEQUENCE public.audit_logs_log_id_seq OWNED BY public.audit_logs.log_id;
          public               postgres    false    229            �            1259    20086 
   categories    TABLE       CREATE TABLE public.categories (
    category_id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
    DROP TABLE public.categories;
       public         heap r       postgres    false            �            1259    20085    categories_category_id_seq    SEQUENCE     �   CREATE SEQUENCE public.categories_category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 1   DROP SEQUENCE public.categories_category_id_seq;
       public               postgres    false    220            w           0    0    categories_category_id_seq    SEQUENCE OWNED BY     Y   ALTER SEQUENCE public.categories_category_id_seq OWNED BY public.categories.category_id;
          public               postgres    false    219            �            1259    20099    products    TABLE       CREATE TABLE public.products (
    product_id integer NOT NULL,
    product_name character varying(100) NOT NULL,
    category_id integer,
    description text,
    unit_price numeric(10,2) NOT NULL,
    cost_price numeric(10,2) NOT NULL,
    stock_quantity integer DEFAULT 0 NOT NULL,
    expiry_date date,
    reorder_level integer DEFAULT 10,
    supplier_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
    DROP TABLE public.products;
       public         heap r       postgres    false            �            1259    20098    products_product_id_seq    SEQUENCE     �   CREATE SEQUENCE public.products_product_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.products_product_id_seq;
       public               postgres    false    222            x           0    0    products_product_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.products_product_id_seq OWNED BY public.products.product_id;
          public               postgres    false    221            �            1259    20134 
   sale_items    TABLE     �   CREATE TABLE public.sale_items (
    item_id integer NOT NULL,
    sale_id integer,
    product_id integer,
    quantity integer NOT NULL,
    unit_price numeric(10,2) NOT NULL,
    discount numeric(10,2) DEFAULT 0,
    subtotal numeric(10,2) NOT NULL
);
    DROP TABLE public.sale_items;
       public         heap r       postgres    false            �            1259    20133    sale_items_item_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sale_items_item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.sale_items_item_id_seq;
       public               postgres    false    226            y           0    0    sale_items_item_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.sale_items_item_id_seq OWNED BY public.sale_items.item_id;
          public               postgres    false    225            �            1259    20117    sales    TABLE     n  CREATE TABLE public.sales (
    sale_id integer NOT NULL,
    invoice_number character varying(50) NOT NULL,
    user_id integer,
    sale_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    total_amount numeric(10,2) NOT NULL,
    payment_method character varying(50),
    notes text,
    cash_tendered numeric(10,2),
    change_amount numeric(10,2)
);
    DROP TABLE public.sales;
       public         heap r       postgres    false            �            1259    20116    sales_sale_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sales_sale_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 (   DROP SEQUENCE public.sales_sale_id_seq;
       public               postgres    false    224            z           0    0    sales_sale_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE public.sales_sale_id_seq OWNED BY public.sales.sale_id;
          public               postgres    false    223            �            1259    20152 	   suppliers    TABLE     z  CREATE TABLE public.suppliers (
    supplier_id integer NOT NULL,
    name character varying(100) NOT NULL,
    contact_person character varying(100),
    phone character varying(20),
    email character varying(100),
    address text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
    DROP TABLE public.suppliers;
       public         heap r       postgres    false            �            1259    20151    suppliers_supplier_id_seq    SEQUENCE     �   CREATE SEQUENCE public.suppliers_supplier_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE public.suppliers_supplier_id_seq;
       public               postgres    false    228            {           0    0    suppliers_supplier_id_seq    SEQUENCE OWNED BY     W   ALTER SEQUENCE public.suppliers_supplier_id_seq OWNED BY public.suppliers.supplier_id;
          public               postgres    false    227            �            1259    20075    users    TABLE     �  CREATE TABLE public.users (
    user_id integer NOT NULL,
    username character varying(50) NOT NULL,
    password character varying(100) NOT NULL,
    role character varying(20) NOT NULL,
    full_name character varying(100) NOT NULL,
    email character varying(100),
    last_login timestamp without time zone,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
    DROP TABLE public.users;
       public         heap r       postgres    false            �            1259    20074    users_user_id_seq    SEQUENCE     �   CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 (   DROP SEQUENCE public.users_user_id_seq;
       public               postgres    false    218            |           0    0    users_user_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;
          public               postgres    false    217            �           2604    20166    audit_logs log_id    DEFAULT     v   ALTER TABLE ONLY public.audit_logs ALTER COLUMN log_id SET DEFAULT nextval('public.audit_logs_log_id_seq'::regclass);
 @   ALTER TABLE public.audit_logs ALTER COLUMN log_id DROP DEFAULT;
       public               postgres    false    229    230    230            �           2604    20089    categories category_id    DEFAULT     �   ALTER TABLE ONLY public.categories ALTER COLUMN category_id SET DEFAULT nextval('public.categories_category_id_seq'::regclass);
 E   ALTER TABLE public.categories ALTER COLUMN category_id DROP DEFAULT;
       public               postgres    false    219    220    220            �           2604    20102    products product_id    DEFAULT     z   ALTER TABLE ONLY public.products ALTER COLUMN product_id SET DEFAULT nextval('public.products_product_id_seq'::regclass);
 B   ALTER TABLE public.products ALTER COLUMN product_id DROP DEFAULT;
       public               postgres    false    221    222    222            �           2604    20137    sale_items item_id    DEFAULT     x   ALTER TABLE ONLY public.sale_items ALTER COLUMN item_id SET DEFAULT nextval('public.sale_items_item_id_seq'::regclass);
 A   ALTER TABLE public.sale_items ALTER COLUMN item_id DROP DEFAULT;
       public               postgres    false    225    226    226            �           2604    20120    sales sale_id    DEFAULT     n   ALTER TABLE ONLY public.sales ALTER COLUMN sale_id SET DEFAULT nextval('public.sales_sale_id_seq'::regclass);
 <   ALTER TABLE public.sales ALTER COLUMN sale_id DROP DEFAULT;
       public               postgres    false    224    223    224            �           2604    20155    suppliers supplier_id    DEFAULT     ~   ALTER TABLE ONLY public.suppliers ALTER COLUMN supplier_id SET DEFAULT nextval('public.suppliers_supplier_id_seq'::regclass);
 D   ALTER TABLE public.suppliers ALTER COLUMN supplier_id DROP DEFAULT;
       public               postgres    false    227    228    228            �           2604    20078    users user_id    DEFAULT     n   ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);
 <   ALTER TABLE public.users ALTER COLUMN user_id DROP DEFAULT;
       public               postgres    false    218    217    218            o          0    20163 
   audit_logs 
   TABLE DATA           �   COPY public.audit_logs (log_id, user_id, action_type, table_affected, record_id, action_details, ip_address, "timestamp") FROM stdin;
    public               postgres    false    230   �M       e          0    20086 
   categories 
   TABLE DATA           \   COPY public.categories (category_id, name, description, created_at, updated_at) FROM stdin;
    public               postgres    false    220   �Y       g          0    20099    products 
   TABLE DATA           �   COPY public.products (product_id, product_name, category_id, description, unit_price, cost_price, stock_quantity, expiry_date, reorder_level, supplier_id, created_at, updated_at) FROM stdin;
    public               postgres    false    222   [       k          0    20134 
   sale_items 
   TABLE DATA           l   COPY public.sale_items (item_id, sale_id, product_id, quantity, unit_price, discount, subtotal) FROM stdin;
    public               postgres    false    226   �_       i          0    20117    sales 
   TABLE DATA           �   COPY public.sales (sale_id, invoice_number, user_id, sale_date, total_amount, payment_method, notes, cash_tendered, change_amount) FROM stdin;
    public               postgres    false    224   a       m          0    20152 	   suppliers 
   TABLE DATA           u   COPY public.suppliers (supplier_id, name, contact_person, phone, email, address, created_at, updated_at) FROM stdin;
    public               postgres    false    228   Pc       c          0    20075    users 
   TABLE DATA           w   COPY public.users (user_id, username, password, role, full_name, email, last_login, is_active, created_at) FROM stdin;
    public               postgres    false    218   Ee       }           0    0    audit_logs_log_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.audit_logs_log_id_seq', 183, true);
          public               postgres    false    229            ~           0    0    categories_category_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.categories_category_id_seq', 20, true);
          public               postgres    false    219                       0    0    products_product_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.products_product_id_seq', 29, true);
          public               postgres    false    221            �           0    0    sale_items_item_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.sale_items_item_id_seq', 43, true);
          public               postgres    false    225            �           0    0    sales_sale_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.sales_sale_id_seq', 19, true);
          public               postgres    false    223            �           0    0    suppliers_supplier_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.suppliers_supplier_id_seq', 9, true);
          public               postgres    false    227            �           0    0    users_user_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.users_user_id_seq', 12, true);
          public               postgres    false    217            �           2606    20171    audit_logs audit_logs_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (log_id);
 D   ALTER TABLE ONLY public.audit_logs DROP CONSTRAINT audit_logs_pkey;
       public                 postgres    false    230            �           2606    20097    categories categories_name_key 
   CONSTRAINT     Y   ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_name_key UNIQUE (name);
 H   ALTER TABLE ONLY public.categories DROP CONSTRAINT categories_name_key;
       public                 postgres    false    220            �           2606    20095    categories categories_pkey 
   CONSTRAINT     a   ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (category_id);
 D   ALTER TABLE ONLY public.categories DROP CONSTRAINT categories_pkey;
       public                 postgres    false    220            �           2606    20110    products products_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (product_id);
 @   ALTER TABLE ONLY public.products DROP CONSTRAINT products_pkey;
       public                 postgres    false    222            �           2606    20140    sale_items sale_items_pkey 
   CONSTRAINT     ]   ALTER TABLE ONLY public.sale_items
    ADD CONSTRAINT sale_items_pkey PRIMARY KEY (item_id);
 D   ALTER TABLE ONLY public.sale_items DROP CONSTRAINT sale_items_pkey;
       public                 postgres    false    226            �           2606    20127    sales sales_invoice_number_key 
   CONSTRAINT     c   ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_invoice_number_key UNIQUE (invoice_number);
 H   ALTER TABLE ONLY public.sales DROP CONSTRAINT sales_invoice_number_key;
       public                 postgres    false    224            �           2606    20125    sales sales_pkey 
   CONSTRAINT     S   ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_pkey PRIMARY KEY (sale_id);
 :   ALTER TABLE ONLY public.sales DROP CONSTRAINT sales_pkey;
       public                 postgres    false    224            �           2606    20161    suppliers suppliers_pkey 
   CONSTRAINT     _   ALTER TABLE ONLY public.suppliers
    ADD CONSTRAINT suppliers_pkey PRIMARY KEY (supplier_id);
 B   ALTER TABLE ONLY public.suppliers DROP CONSTRAINT suppliers_pkey;
       public                 postgres    false    228            �           2606    20082    users users_pkey 
   CONSTRAINT     S   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public                 postgres    false    218            �           2606    20084    users users_username_key 
   CONSTRAINT     W   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);
 B   ALTER TABLE ONLY public.users DROP CONSTRAINT users_username_key;
       public                 postgres    false    218            �           2606    20172 "   audit_logs audit_logs_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);
 L   ALTER TABLE ONLY public.audit_logs DROP CONSTRAINT audit_logs_user_id_fkey;
       public               postgres    false    218    230    4793            �           2606    20111 "   products products_category_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(category_id);
 L   ALTER TABLE ONLY public.products DROP CONSTRAINT products_category_id_fkey;
       public               postgres    false    4799    222    220            �           2606    20146 %   sale_items sale_items_product_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.sale_items
    ADD CONSTRAINT sale_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(product_id);
 O   ALTER TABLE ONLY public.sale_items DROP CONSTRAINT sale_items_product_id_fkey;
       public               postgres    false    4801    222    226            �           2606    20141 "   sale_items sale_items_sale_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.sale_items
    ADD CONSTRAINT sale_items_sale_id_fkey FOREIGN KEY (sale_id) REFERENCES public.sales(sale_id);
 L   ALTER TABLE ONLY public.sale_items DROP CONSTRAINT sale_items_sale_id_fkey;
       public               postgres    false    226    4805    224            �           2606    20128    sales sales_user_id_fkey    FK CONSTRAINT     |   ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);
 B   ALTER TABLE ONLY public.sales DROP CONSTRAINT sales_user_id_fkey;
       public               postgres    false    224    4793    218            o     x��[�n#�}�|� �ٮ����m}�#^� ��#qe"���x�5�_ʗ�T�"��P˞?�F�S5�u;U-������l~�a5]��ӛ��|d?���������-��RK�]�c}�����Kc���xu6�[��������{�]a>�c�y:���&���O#qw�ς�� �����a��kyt�=Z=,��Y)�������'�-���.Zw����7��l����l�~�,���d9};o�vv��~4�d*�qg�=�G�A^�:]Ȟ��ů{�6����tI{`���q3^�35��f9-�n��g���ۿ����
�r΅�F��Ň9��OQ���7���6�}��dy7����5�.`�n�����.=}3�?��.>y>R��n�Z���I���Bt��8wO�����ޫp1��o)O�!�W������x���|�,��G���G��#����b�����_�8Jj�w������f�¶�7�!S����j�[o�nch���rH���6rL�
�qޞ��ػV8E��o��6&L'xk�x���&�#D��m�	Sl(8l
cM-kt
�|�æh^�r��7�^�I�U"Ն��Z�.(�/\T��A�k9:����čAr�)��֗�-��[���@Жs"�� uc��0)D�Ȑ� �r�d���o^)��F�0���?M�P-��_;m);KJuQX#@���5"��P��t�C������.z����>[JF�͍Xu�T����u�B�F��� -;e�Ie� ���Ě�^
v�R.�����V�Z'.��x�_��	E,u�����2���P��C���J-�a��T�6��ء��ӏ�r�+??��>^Mo�Ս_�׬^�0����z�:~zw7�On�wH��V�Vӻ�0�	o?ޮ>�j��吢�����c�YR˶^���Ѷ��d�C8�9@�^C�P5�� ��� �̖ݭc���-7�d������Xϫ=\l�u���]��<a�5�o�[�x���2�;b&�-u#�)S�C�܇1I�A=c�C�x�CǒR�T[P6	@��S�еI�Ya�!!��$�7(�HiZB�of�M��	�ϿO���^T�tp��h�G��Z�l��s��#�TK��	M?J$�F�#�nj�9	�8�#������fw���(�	ԁ]}�����va�o��!X]OV=��0&�hh�P��M��'�C HG�� M��ڎ4��-��~�4��*�Y�&�@1+�b�=P�&�GY9TAd��Dɑ3��&���Fc'IX|�RC�aB����DVِ�s��q�C��T_tv�XX��&� @��1�3Ԋ�������WO��X]!4-��8$"lP�&���&ʑ���>��P<�R��K@`� \há��+ӫ0"W�)J"mb5��'c`.��p�0�#*�)��&���X��\P��&��1Q+={�Pne��E�ز8 �� ��Ek.8Kmu�`W����Z�^DDr�N�T��p�O}c�g���5��.���|��M^)
HJ��w�y�����N����a2�2��?p������;B;���ϖ����nzQ5��&7���@Y��8�&�//�kH4�O��^
�x�������7j�9��?���,D�q�&w+ɮ�G:�#�j.�>ƻ>���T��>ۯ�ۼR��������T΁H�&�Q�i� ��:%���M~��
E'��y�F}s�VI)���,U_I��M��ʤ>�^K壖B��]��ZZ��l�zsNOb8fz�LG������{���mJ�sc{�/G$�,`T� �h�I����)ȏ-"���=`�[C�`b/���t��aKr�� ���Ή�W�͗l�B����n<+Y* +��X�8w[�kLh�|`3t��.�c�>,�٩��q|ca�)Y��?W�kf!)�ψ%�/��1ŷIM�Y���B�
sD�CU��`_�mwp�!;�!�8m!Դ`o�IR��o!J>%�Egz�`���r&D[�QY��OV�?��w��j��E�i�xT��/��[G�ߎGrLޒ�:%o��՚��E���Ψ������Ht�<��o!T�N$�>\C�kJeR1��B�Xc+��ćp��D��ʠ[���je�$A3�$��;Ҳj2�m�Q������9Y� DM����Ԓ:aԉ��"تPC��+Um���g�������n�>$g��tۊ5��5ã?��W��g���^T��W��M�I�BR��ͩ��<yE)\�Z��k�l��jѽE`��#F-Īݏޗ;#oD�{�m1P":)��NFyW��P�e}
>ع�i�()J+�2$X4�u'���`۩����E��O�bD�6f�A�V��&71� ����ʴ�yo7�|���.[����7���o�>s�kI�[�2�UA=�$�9;�t��)���S��ٟ-p I��N�
�I_4��`zn�d�~x��y���1�¡��m�h��#f�ΨlY<e�k+tH`zR7�o6�!����:Ed���^��;7w�=wu'�ru�:Ww ��GL��U�2�1(����QH��k}��-�#c"k��\�^JwM���I�c4�9��Q�6O��Q�̰)T���
��TS>AS�i��������R+Hbg��s �5�>��,�P��5"����]e�e����չ^Ah���˪��b����Q�׻뮮�]u_W[�CI�'6���OO���ɶW����dC��M���]24#l��z��U6��l�7��_W�J
�Y\�b�	8�ќ��%�_Z*Wz ������#��d�^mwMO0Y:�d��&�M1���H�|�n�K3	�_[���BD[�#s�M`���L������=�m+:�8+AⰨ�ۃ�Ʀ��(��/]^���<��3x��dqS��0�*mf�F�c}@�>Xr��é.��BG�-��T��GA��	i���%7 �&���;�t�hs�tPI������I�b9�b�Q�#�f��T��.-⠔<{7z�,����5�V��ej~k���?>c�      e   F  x���1o�0�g�W���8�B6D�X*!U����G�6�#���_�H��CF����ggbc���t�hH+&gt����J3zR5�=�����b��<�lUi�X͗�2+�?�DF��+�Ȃǚ�B���6���� C��NΏr�؂S9�N������=��mkl�r�����pFU�y"�;�aCF�3��?:�qI���4Y�R�}����=%�]��T�@#c��j�H{[�Ugx����CDCK^�����Y�O|kL1���ĝB�S}`l�B�&�(S��+B�b7\�������\�y1ϋt�^�SJ>�I�|���*      g   �  x��W�n#7<S_�Kn��׼t���7��i/�%�*���ק�3����X��Ů�겨ȥ�;�ۚpr�7����c����D�d�Rr�3��+~��_P!ֲZ+�b��B��H�5W+VV\���y�b?��]��0��E��MC{�n���^�?��Ҍ��*"E^��Œ�%@�9���u&�B����⿎B��.��6�Io��=)ɍ���7C�(@��k,���w�X����)�x5Qș($����ο����Pp��_����(�n���O��(WEF�8	�	#���m  Rd @�o~	�Y�ӄԉ����v�	$G�.�R Slv/@4��UG�ţw���nb����� a�B �Z!lj[b'(j�tm�n����}ئ��5�!)�#BS#J3g�)ɷ�G�{����ᛯn��V솈Bu��*AH�*��^�gT̈́P��>�GMJ�GЎ6VoL4=mMc�D�	� Tˑ���%:��p��t�#�}�[���3#Q�Y�*��F^N͈�Y��2�_����|��(�q t�����;�ޖ����f���E�_m��e��po���� r��*�0$ŝ�mE�6���L���xqw&|�$}J����D��=H������=��H*o�=�}�v�?+�J�%0�|E�~���:v�3pս�vK]G��`�c��2�OM�g9�s�08�<n�|��]d��km�mOO㴨xr�"M�'r�A��̼�}�}�w���"p~���8h �C�5����.dۛ=��d$=d�pFw��o?tM �BS�s\�"�1�v8y/���n:&�!�ǣI�Su%���x���?'��%z�{��]b���Қ��#Y2^U��r��	��,f{,|�n)�m
�� g"(��XC.؁$S*�m��њ��D�$5�x�Mo�A��N���im��8hH'�@ z`�
����ٶ�G>�U��T�K�K�L�P���û��0��W7=F�3t��p��A�Y�!4�W�H&�\�a��a%��8#��!!L��Q�ǐזi[�zl�M�ҿB(Y.Jr�lk0��n)�<n�77�DҦCʸ+�T��"g�W9"�`�˼Pj�}�X,�d��      k   3  x�mS˭�0;K��ر����G:m��9`EȤ(�ťJH+s�3q/sh��$��:`�D��G&�@Iz�P������5;�qՉ�@9�\�7������հ�Nz�:�P�_��'���Hx1���sf�}�">L�_�H�Aþ�<������'���-�����e�#�3�0�!kTtn���&3��Bi ���"V��
���@�k�����iB��ז����,��HŊ|/��<H%S�#�:����M���a�9�֠�ۓ< 7�d�i��
t�P�y�+������<{|+'����+����J      i   9  x�m��n�0��~���r��e��=쩗���U���I SW� �������W4�  ��{�B�\"�xj���Ӿ�M/7�a�>�^���ҹ�����-�hj�d�0Y}�ݏ�鷳����PA"�f
�
,~��W�o�M�?���(���.���)��ra�ek=�"���g����z
�Y A��T���^��V>7���8�u���'��4un�<4u>��hz�q>��ӹ���:�/<�%�NwHZ��{A!(�
�?���W��%��Rտ����G���0�Mw·Q^�s/��f�z��p?�^w.>��i��[�U��aڤf��K�]ͨ�}tF��Ȱk��W���R�d������@���8V�*�B3��WC,�:ri:����=��B�R2Q��x��ņ�\ڃB���~�Q�ȻT��k3��M�-8�gk@����K���<��u迂6� ��D������ ��ۮ9��Ϧ�[fg@�x�Ϗ�r�HB|�C�Yi$�cݘ�)�
�̅��%o:� iC9�h�������2�      m   �  x���͎�0E��)�e�&Q�?��餂)��NG��d\bƎ#�a���#U7�]��c��+S�i�Q��;&�l�|�M��!�����O��O�lL�@�"��"C�w��@��΃��ڼ��3�0)��(��ԏ)��4��0h����("k�"*ݛ��ʽ�b�5p����Fq����sZ(d������I����۞{��f�Kn=X� ��0&���ڃ%k��an���8I}T̉¨h��1�'.e˭��<��V#j���+���F��|�I�Npٺ�Ã�%+a,�Qث#6�IH$F����R8o�$,�8b����N�l�x|k�)Y0�7�����C?��Q�q�$�_C��>�Qb������?��Q3�p-�ܭ �鍂9�W���/K�1zo�R�X�y�eQ����,�_?n;~��A(u:�b���<��������`����u����l�iI�3'��F?��h�-�-      c   n  x����N� ů�O�,��t[�4�^l�1��C��-����o/m��_v5!�3C��w@@��ޚ���1����(�b)���v$����3��~����Hk� �+V�^(�V4/YQ M��Y*��1ʰ�k�q��un��7��f�<�9�-e���i|G���Y���h��?�m��|����j�/ו84���b-rDQe6x�}�U�K�jw�ڶm�a7�c�K�i���@τ��|7��82�d���r�DԂ$7���k�9�����b-E!K�I����j_bb9��W>8�������Y�?��ӯ|?R�R��ΐKo�I���bJ2*0�y�{���ƣh׶�kӒ�V�gp�:���*�>�Ͳ��-��     