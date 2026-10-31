package com.pou.routepou.pairing

import com.wireguard.crypto.KeyPair

/** Uses the official WireGuard crypto implementation; no custom cryptography. */
object RoutePouWgKeys {
    fun generate(): RoutePouWgConfig.Keys {
        val server = KeyPair()
        val client = KeyPair()
        return RoutePouWgConfig.Keys(
            server.privateKey.toBase64(), server.publicKey.toBase64(),
            client.privateKey.toBase64(), client.publicKey.toBase64()
        )
    }
}
