create table
  public.shop_inventory (
    id bigint generated by default as identity,
    gold integer not null,
    red_ml integer not null,
    green_ml integer not null,
    blue_ml integer not null,
    dark_ml integer not null,
    constraint shop_inventory_pkey primary key (id),
    constraint shop_inventory_id_key unique (id)
  ) tablespace pg_default;

create table
  public.potion_inventory (
    potion_id bigint generated by default as identity,
    sku text not null,
    type integer[] not null,
    num integer not null,
    cost integer not null,
    name text not null,
    constraint V3_global_inventory_pkey primary key (potion_id),
    constraint potion_inventory_name_key unique (name),
    constraint potion_inventory_potion_id_key unique (potion_id),
    constraint potion_inventory_sku_key unique (sku),
    constraint potion_inventory_type_key unique (
      type
    )
  ) tablespace pg_default;

  create table
  public.carts (
    cart_id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    name text null,
    constraint carts_pkey primary key (cart_id),
    constraint carts_cart_id_key unique (cart_id)
  ) tablespace pg_default;

  create table
  public.cart_items (
    cart_id bigint generated by default as identity,
    potion_id bigint not null,
    quantity integer not null,
    sku text not null,
    constraint cart_items_pkey primary key (cart_id, potion_id)
  ) tablespace pg_default;

  